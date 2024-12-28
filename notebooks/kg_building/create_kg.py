import sys
import json 
import joblib
import gc
from tqdm import tqdm
import os
from typing import List, Dict, Tuple

# TO CHANGE
BASEDIR = "../../"
sys.path.insert(0, BASEDIR)

from src.pipelines.memorize import MemPipelineConfig, MemPipeline, LLMExtractorConfig, LLMUpdatorConfig
from src.kg_model import KnowledgeGraphModel, EmbeddingsModelConfig, GraphModelConfig, EmbedderModelConfig
from src.db_drivers.graph_driver import GraphDBConnectionConfig, GraphDriverConfig
from src.db_drivers.vector_driver import VectorDBConnectionConfig, VectorDriverConfig

# gigachat key
#GIGACHAT_CREDS = 'OWUwOGUzOWEtMjJiNi00YmMxLThmMmItNzMwNjM2MTI2YmYxOjg2ODdiOTVhLTZkNDctNGFjOC1iMmViLTEyNDA5MmFiN2Q5Mw=='
# openai key
#API_KEY = "'sk-861mINAavom2SSBqgrI82D4thMOfqT37knCof2o0H0T3BlbkFJ2gdVXJuVjNesNNP2aeUwPoBpZP3a3R1gn1kqv97CsA'"

gc.collect()

###################

# TO CHANGE
HYPER_PARAMS = {
    'DATASET_PATH': '../../data/qa_datasets/diaasqa/Augment_DiaASQ.json',
    'DATASET_NAME': 'diaasqa',
    'KNOWLEDGE_GRAPH_NAME': 'gigachat_filtered',
    'EMBEDDER_MODEL_PATH': '../../models/intfloat/multilingual-e5-small',
    'DELETE_OBSOLETE_INFO': True
}
# TO CHANGE

BASE_PATH = "../../data/knowledge_graphs/"
DATASET_PATH = BASE_PATH + f"{HYPER_PARAMS['DATASET_NAME']}/"
KG_PATH = DATASET_PATH + f"{HYPER_PARAMS['KNOWLEDGE_GRAPH_NAME']}/"

HYPER_PARAMS_PATH = KG_PATH + 'hyperparameters.json'
EXTRACTED_TRIPLETS_PATH = KG_PATH + "extracted_triplets"
GRAPH_DRIVER_CONFIG_PATH = KG_PATH + "graph_config"
EMBEDDINGS_DRIVER_CONFIG_PATH = KG_PATH + "embeddings_config"
MEM_PIPELINE_CONFIG_PATH = KG_PATH + "mem_pipeline_config"

VECTORIZED_DB_PATH = KG_PATH + "embeddings_part/"
GRAPH_DB_PATH = KG_PATH + "graph_part/"

####################3

if not os.path.exists(BASE_PATH):
    raise ValueError(f"Директории не существует: {BASE_PATH}")
if not os.path.exists(DATASET_PATH):
    raise ValueError(f"Директории не существует: {DATASET_PATH}")
if os.path.exists(KG_PATH):
    raise ValueError(f"Директория существует: {KG_PATH}")

os.mkdir(KG_PATH)
os.mkdir(VECTORIZED_DB_PATH)
os.mkdir(GRAPH_DB_PATH)

print(VECTORIZED_DB_PATH)
print(GRAPH_DB_PATH)

out = input("continue? ")

##############

with open(HYPER_PARAMS_PATH, 'w', encodings='utf-8') as fd:
    fd.write(json.dumps(HYPER_PARAMS, ensure_ascii=False, indent=1))

##############

# Setting knowledge graph

graph_config = GraphModelConfig(
    driver_config=GraphDriverConfig(
        db_vendor='neo4j', 
        db_config=GraphDBConnectionConfig(
            uri="bolt://0.0.0.0:7687", params={'user': "neo4j", 'pwd': 'password'}, 
            need_to_clear=True)))

embed_config = EmbeddingsModelConfig(
    nodesdb_driver_config=VectorDriverConfig(
        db_vendor='chroma',
        db_config=VectorDBConnectionConfig(
            path=VECTORIZED_DB_PATH, db_info={'db': 'personalaidb', 'table': "vectorized_nodes"}, need_to_clear=True)),
    tripletsdb_driver_config=VectorDriverConfig(
        db_vendor='chroma', 
        db_config=VectorDBConnectionConfig(
            path=VECTORIZED_DB_PATH, db_info={'db': 'personalaidb', 'table': "vectorized_triplets"}, need_to_clear=True)),
    embedder_config=EmbedderModelConfig(model_name_or_path=HYPER_PARAMS['EMBEDDER_MODEL_PATH']))

kg_model = KnowledgeGraphModel(
    graph_config=graph_config,
    embeddings_config=embed_config)

print(kg_model.embeddings_struct.vectordbs['nodes'].count_items())
print(kg_model.embeddings_struct.vectordbs['triplets'].count_items())
print(kg_model.graph_struct.db_conn.count_items())

# Setting Memorization Pipeline
mem_config = MemPipelineConfig(
    extractor_config=LLMExtractorConfig(),
    updator_config=LLMUpdatorConfig(
        delete_obsolete_info=HYPER_PARAMS['DELETE_OBSOLETE_INFO']))

mem_pipeline = MemPipeline(kg_model, mem_config)

########################

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

########################

saved_triplets = []
for item in tqdm(dataset):
    text, properties = item[0], item[1]
    extracted_triplets, _ = mem_pipeline.remember(text, properties)
    saved_triplets.append(extracted_triplets)

########################

joblib.dump(saved_triplets, EXTRACTED_TRIPLETS_PATH)
