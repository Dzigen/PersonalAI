import sys
import json
import joblib
import gc
from tqdm import tqdm
import yaml
import os
from typing import List, Dict, Tuple

BASEDIR = '/home/m.menschikov/workspace/Personal-AI' # TO CHANGE
sys.path.insert(0, BASEDIR)

from src.pipelines.memorize import MemPipelineConfig, MemPipeline, LLMExtractorConfig, LLMUpdatorConfig
from src.kg_model import KnowledgeGraphModel, EmbeddingsModelConfig, GraphModelConfig
from src.db_drivers.graph_driver import GraphDriverConfig
from src.db_drivers.vector_driver import VectorDriverConfig

# gigachat key
#GIGACHAT_CREDS = 'OWUwOGUzOWEtMjJiNi00YmMxLThmMmItNzMwNjM2MTI2YmYxOjg2ODdiOTVhLTZkNDctNGFjOC1iMmViLTEyNDA5MmFiN2Q5Mw=='
# openai key
#API_KEY = "'sk-861mINAavom2SSBqgrI82D4thMOfqT37knCof2o0H0T3BlbkFJ2gdVXJuVjNesNNP2aeUwPoBpZP3a3R1gn1kqv97CsA'"

gc.collect()

########SETTING HYPERPARAMS###########

# Read YAML file
CREATE_DIR_PATH = f'{BASEDIR}/notebooks/kg_building/create'
PARAMS_FILE_PATH = f'{CREATE_DIR_PATH}/params.yaml'

with open(PARAMS_FILE_PATH, 'r') as stream:
    HYPER_PARAMS = yaml.safe_load(stream)

BASE_PATH = f"{BASEDIR}/data/knowledge_graphs/"
DATASET_PATH = BASE_PATH + f"{HYPER_PARAMS['DATASET_NAME']}/"
KG_PATH = DATASET_PATH + f"{HYPER_PARAMS['KNOWLEDGE_GRAPH_NAME']}/"

HYPER_PARAMS_PATH = KG_PATH + 'hyperparameters.json'
EXTRACTED_TRIPLETS_PATH = KG_PATH + "extracted_triplets"
GRAPH_DRIVER_CONFIG_PATH = KG_PATH + "graph_config"
EMBEDDINGS_DRIVER_CONFIG_PATH = KG_PATH + "embeddings_config"
MEM_PIPELINE_CONFIG_PATH = KG_PATH + "mem_pipeline_config"

VECTORIZED_DB_PATH = KG_PATH + "embeddings_part/"
GRAPH_DB_PATH = KG_PATH + "graph_part/"

TMP_EXTRACTED_TRIPLETS_PATH = KG_PATH + "tmp_extracted_triplets_path/"

GRAPHDB_CONFIG_PATH = f"{CREATE_DIR_PATH}/graphdb_config"
EMBEDDER_CONFIG_PATH = f"{CREATE_DIR_PATH}/embedder_config"
NODESDB_CONFIG_PATH = f"{CREATE_DIR_PATH}/nodesdb_config"
TRIPLETSDB_CONFIG_PATH = f"{CREATE_DIR_PATH}/tripletsdb_config"

###########FOLDERS INIT#########3

if HYPER_PARAMS['init_struct']:

    if not os.path.exists(BASE_PATH):
        raise ValueError(f"Директории не существует: {BASE_PATH}")
    if not os.path.exists(DATASET_PATH):
        raise ValueError(f"Директории не существует: {DATASET_PATH}")
    if os.path.exists(KG_PATH):
        raise ValueError(f"Директория существует: {KG_PATH}")
    if os.path.exists(TMP_EXTRACTED_TRIPLETS_PATH):
        raise ValueError(f"Директория существует: {TMP_EXTRACTED_TRIPLETS_PATH}")

    os.mkdir(KG_PATH)
    os.mkdir(VECTORIZED_DB_PATH)
    os.mkdir(GRAPH_DB_PATH)
    os.mkdir(TMP_EXTRACTED_TRIPLETS_PATH)

print(VECTORIZED_DB_PATH)
print(GRAPH_DB_PATH)

##############

# Setting knowledge graph

graphdb_config = joblib.load(GRAPHDB_CONFIG_PATH)
graphdb_config.need_to_clear = HYPER_PARAMS['knowledge_graph']['need_to_clear']

nodesdb_config = joblib.load(NODESDB_CONFIG_PATH)
nodesdb_config.need_to_clear = HYPER_PARAMS['knowledge_graph']['need_to_clear']

tripletsdb_config =  joblib.load(TRIPLETSDB_CONFIG_PATH)
tripletsdb_config.need_to_clear = HYPER_PARAMS['knowledge_graph']['need_to_clear']

embedder_config = joblib.load(EMBEDDER_CONFIG_PATH)

graph_config = GraphModelConfig(
    driver_config=GraphDriverConfig(
        db_vendor=HYPER_PARAMS['knowledge_graph']['graphdb_vendor'],
        db_config=graphdb_config))

embed_config = EmbeddingsModelConfig(
    nodesdb_driver_config=VectorDriverConfig(
        db_vendor=HYPER_PARAMS['knowledge_graph']['nodesdb_vendor'],
        db_config=nodesdb_config),
    tripletsdb_driver_config=VectorDriverConfig(
        db_vendor=HYPER_PARAMS['knowledge_graph']['tripletsdb_vendor'],
        db_config=tripletsdb_config),
    embedder_config=embedder_config)

kg_model = KnowledgeGraphModel(
    graph_config=graph_config,
    embeddings_config=embed_config)

print(kg_model.embeddings_struct.vectordbs['nodes'].count_items())
print(kg_model.embeddings_struct.vectordbs['triplets'].count_items())
print(kg_model.graph_struct.db_conn.count_items())

# Setting Memorization Pipeline
mem_config = MemPipelineConfig(
    extractor_config=LLMExtractorConfig(lang=HYPER_PARAMS['LANG']),
    updator_config=LLMUpdatorConfig(
        lang=HYPER_PARAMS['LANG'],
        delete_obsolete_info=HYPER_PARAMS['DELETE_OBSOLETE_INFO']))

mem_pipeline = MemPipeline(kg_model, mem_config)

############SAVING HYPERPARAMS############

with open(HYPER_PARAMS_PATH, 'w', encoding='utf-8') as fd:
    fd.write(json.dumps(HYPER_PARAMS, ensure_ascii=False, indent=1))

joblib.dump(graph_config, GRAPH_DRIVER_CONFIG_PATH)
joblib.dump(embed_config, EMBEDDINGS_DRIVER_CONFIG_PATH)
joblib.dump(mem_config, MEM_PIPELINE_CONFIG_PATH)

########################

def custom_diaasqa_load(dataset_path: str) -> List[Tuple[str, Dict[str, str]]]:
    with open(dataset_path, 'r', encoding='utf-8') as fd:
        data = json.loads(fd.read())

    data_pairs = []
    for item in data['data']:
        data_pairs.append((item['text_dialog'], {'time': item['time'].split(',')[0]}))

    return data_pairs

CUSTOM_LOAD_FUNCS = {
    'diaasqa': custom_diaasqa_load
}
dataset = CUSTOM_LOAD_FUNCS[HYPER_PARAMS['DATASET_NAME']](HYPER_PARAMS['DATASET_PATH'])
print(len(dataset))

###########KG BUILDING#############

for i in tqdm(range(len(dataset))):
    text, properties = dataset[i][0], dataset[i][1]
    extracted_triplets, _ = mem_pipeline.remember(text, properties)

    joblib.dump(extracted_triplets, TMP_EXTRACTED_TRIPLETS_PATH + f'item{i}')

###########ACCUMULATING EXTRACTED TRIPLETSs#############

accum_triplets = []
extracted_t_files = os.listdir(TMP_EXTRACTED_TRIPLETS_PATH)
for t_file in tqdm(extracted_t_files):
    accum_triplets.append(joblib.load(TMP_EXTRACTED_TRIPLETS_PATH + t_file))

joblib.dump(accum_triplets, EXTRACTED_TRIPLETS_PATH)
