import sys
import json
import joblib
import gc
from tqdm import tqdm
import yaml
import os
from typing import List, Dict, Tuple
import pandas as pd

# Read YAML file
CREATE_DIR_PATH = sys.orig_argv[1]
PARAMS_FILE_PATH = f'{CREATE_DIR_PATH}/params.yaml'
with open(PARAMS_FILE_PATH, 'r') as stream:
    HYPER_PARAMS = yaml.safe_load(stream)

# Корневая директория PersonalAI-проекта,
# где лежит исходный код библиотеки (src-каталог)
sys.path.insert(0, HYPER_PARAMS['BASE_PERSONALAI_DIR'])

from src.pipelines.memorize import MemPipelineConfig, MemPipeline, LLMExtractorConfig, LLMUpdatorConfig
from src.kg_model import KnowledgeGraphModel, EmbeddingsModelConfig, GraphModelConfig
from src.db_drivers.graph_driver import GraphDriverConfig, GraphDBConnectionConfig
from src.db_drivers.vector_driver import VectorDriverConfig, VectorDBConnectionConfig, EmbedderModelConfig
from src.db_drivers.kv_driver import KeyValueDriverConfig, KVDBConnectionConfig

from src.pipelines.memorize.extractor.configs import AgentThesisExtrTaskConfigSelector, AgentTripletExtrTaskConfigSelector
from src.pipelines.memorize.updator.configs import AgentReplSimpleTripletTaskConfigSelector, AgentReplThesisTripletTaskConfigSelector
from src.agents import AgentDriverConfig
from src.agents.utils import AgentConnectorConfig

# gigachat key
#GIGACHAT_CREDS = 'OWUwOGUzOWEtMjJiNi00YmMxLThmMmItNzMwNjM2MTI2YmYxOjg2ODdiOTVhLTZkNDctNGFjOC1iMmViLTEyNDA5MmFiN2Q5Mw=='
# openai key
#API_KEY = "'sk-861mINAavom2SSBqgrI82D4thMOfqT37knCof2o0H0T3BlbkFJ2gdVXJuVjNesNNP2aeUwPoBpZP3a3R1gn1kqv97CsA'"

gc.collect()

########SETTING HYPERPARAMS###########

DATASET_PATH = f"{HYPER_PARAMS['KGS_BASE_PATH']}/{HYPER_PARAMS['DATASET_NAME']}"
KG_PATH = DATASET_PATH + f"{HYPER_PARAMS['KNOWLEDGE_GRAPH_NAME']}"

VECTORIZED_DB_PATH = f"{KG_PATH}/{HYPER_PARAMS['KG_DIR_STRUCT']['embeddings_dir_name']}/"
GRAPH_DB_PATH = f"{KG_PATH}/{HYPER_PARAMS['KG_DIR_STRUCT']['graph_dir_name']}/"
KV_DB_PATH = f"{KG_PATH}/{HYPER_PARAMS['KG_DIR_STRUCT']['cache_dir_name']['base']}/"
PERSISTENT_DB_PATH = KV_DB_PATH + f"{HYPER_PARAMS['KG_DIR_STRUCT']['cache_dir_name']['persistant']}/"
RAM_DB_PATH = KV_DB_PATH + f"{HYPER_PARAMS['KG_DIR_STRUCT']['cache_dir_name']['ram_volume']}/"
TMP_EXTRACTED_TRIPLETS_PATH = f"{KG_PATH}/{HYPER_PARAMS['KG_DIR_STRUCT']['tmp_triplets_dir_name']}/"

HYPER_PARAMS_PATH = f"{KG_PATH}/hyperparameters.yaml"
EXTRACTED_TRIPLETS_PATH = f"{KG_PATH}/extracted_triplets"
GRAPH_DRIVER_CONFIG_PATH = f"{KG_PATH}/graph_config"
EMBEDDINGS_DRIVER_CONFIG_PATH = f"{KG_PATH}/embeddings_config"
MEM_PIPELINE_CONFIG_PATH = f"{KG_PATH}/mem_pipeline_config"

# if HYPER_PARAMS['need_to_clear']:
#     u_answer = input("Are you sure is need to clear knowledge graph? (y/n): ")
#     if u_answer == 'n':
#         raise AssertionError
#     elif u_answer == 'y':
#         pass
#     else:
#         raise ValueError
# else:
#     u_answer = input("Are you sure is no need to clear knowledge graph? (y/n): ")
#     if u_answer == 'n':
#         raise AssertionError
#     elif u_answer == 'y':
#         pass
#     else:
#         raise ValueError

########Setting knowledge graph######

# Graph model config

graphdb_config = GraphDBConnectionConfig(
    host=HYPER_PARAMS['KG_DB_CONFIGS']['graphdb_config']['host'],
    port=HYPER_PARAMS['KG_DB_CONFIGS']['graphdb_config']['port'],
    db_info=HYPER_PARAMS['KG_DB_CONFIGS']['graphdb_config']['db_info'],
    params=HYPER_PARAMS['KG_DB_CONFIGS']['graphdb_config']['params'],
    need_to_clear=HYPER_PARAMS['KG_DB_CONFIGS']['need_to_clear']
)

gmodel_config = GraphModelConfig(
    driver_config=GraphDriverConfig(
        db_vendor=HYPER_PARAMS['KG_DB_CONFIGS']['graphdb_config']['vendor'],
        db_config=graphdb_config))

# Vector model config

nodesdb_config = VectorDBConnectionConfig(
    db_info=HYPER_PARAMS['KG_DB_CONFIGS']['nodesdb_config']['db_info'],
    path=VECTORIZED_DB_PATH,
    need_to_clear=HYPER_PARAMS['KG_DB_CONFIGS']['need_to_clear']
)

tripletsdb_config = VectorDBConnectionConfig(
    db_info=HYPER_PARAMS['KG_DB_CONFIGS']['tripletsdb_config']['db_info'],
    path=VECTORIZED_DB_PATH,
    need_to_clear=HYPER_PARAMS['KG_DB_CONFIGS']['need_to_clear']
)

embedder_config = EmbedderModelConfig(
    model_name_or_path=HYPER_PARAMS['KG_DB_CONFIGS']['embedder_config'],
    prompts=HYPER_PARAMS['KG_DB_CONFIGS']['prompts']
)

emodel_config = EmbeddingsModelConfig(
    nodesdb_driver_config=VectorDriverConfig(
        db_vendor=HYPER_PARAMS['KG_DB_CONFIGS']['nodesdb_config']['vendor'],
        db_config=nodesdb_config),
    tripletsdb_driver_config=VectorDriverConfig(
        db_vendor=HYPER_PARAMS['KG_DB_CONFIGS']['tripletsdb_config']['vendor'],
        db_config=tripletsdb_config),
    embedder_config=embedder_config)

# KG model

kg_model = KnowledgeGraphModel(
    graph_config=gmodel_config,
    embeddings_config=emodel_config)

# print init info

print(kg_model.embeddings_struct.vectordbs['nodes'].count_items())
print(kg_model.embeddings_struct.vectordbs['triplets'].count_items())
print(kg_model.graph_struct.db_conn.count_items())

########SETTING MEMORIZE PIPELINE######

# agent driver config
adriver_config = AgentDriverConfig(
    name=HYPER_PARAMS['MEM_PIPELINE_CONFIG']['agent_config']['vendor'],
    agent_config=AgentConnectorConfig(
        gen_strategy=HYPER_PARAMS['MEM_PIPELINE_CONFIG']['gen_strategy'],
        credentials=HYPER_PARAMS['MEM_PIPELINE_CONFIG']['credentials'],
        ext_params=HYPER_PARAMS['MEM_PIPELINE_CONFIG']['ext_params']
    )
)

# cache driver config
if HYPER_PARAMS['MEM_PIPELINE_CONFIG']['llm_caching']:
    kvdriver_config = KeyValueDriverConfig(
        db_vendor='mixed_kv',
        db_config=KVDBConnectionConfig(
            params={
                'redis_config': KVDBConnectionConfig(
                    host=HYPER_PARAMS['MEM_PIPELINE_CONFIG']['ram_cache_config']['host'],
                    port=HYPER_PARAMS['MEM_PIPELINE_CONFIG']['ram_cache_config']['port'],
                    db_info=HYPER_PARAMS['MEM_PIPELINE_CONFIG']['ram_cache_config']['db_info'],
                    params=HYPER_PARAMS['MEM_PIPELINE_CONFIG']['ram_cache_config']['params']),
                'mongo_config': KVDBConnectionConfig(
                    host=HYPER_PARAMS['MEM_PIPELINE_CONFIG']['persistent_cache_config']['host'],
                    port=HYPER_PARAMS['MEM_PIPELINE_CONFIG']['persistent_cache_config']['port'],
                    db_info=HYPER_PARAMS['MEM_PIPELINE_CONFIG']['persistent_cache_config']['db_info'],
                    params=HYPER_PARAMS['MEM_PIPELINE_CONFIG']['persistent_cache_config']['params'])
            }
        )
    )
else:
    kvdriver_config = None

# extractor stage config
extractor_config = LLMExtractorConfig(
    lang=HYPER_PARAMS['MEM_PIPELINE_CONFIG']['lang'],
    adriver_config=adriver_config,
    triplets_extraction_task_config=AgentTripletExtrTaskConfigSelector.select(
        base_config_version=HYPER_PARAMS['MEM_PIPELINE_CONFIG']['extractor_stage']['extract_triplets']['prompts_version'],
        kvcache_driver_config=kvdriver_config),
    thesises_extraction_task_config=AgentThesisExtrTaskConfigSelector.select(
        base_config_version=HYPER_PARAMS['MEM_PIPELINE_CONFIG']['extractor_stage']['extract_thesises']['prompts_version'],
        kvcache_driver_config=kvdriver_config),
)

# updator stage config
updator_config = LLMUpdatorConfig(
    lang=HYPER_PARAMS['MEM_PIPELINE_CONFIG']['lang'],
    adriver_config=adriver_config,
    replace_simple_task_config=AgentReplSimpleTripletTaskConfigSelector.select(
        base_config_version=HYPER_PARAMS['MEM_PIPELINE_CONFIG']['updator_stage']['replace_simple_triplets']['prompts_version'],
        kvcache_driver_config=kvdriver_config),
    replace_thesis_task_config= AgentReplThesisTripletTaskConfigSelector.select(
        base_config_version=HYPER_PARAMS['MEM_PIPELINE_CONFIG']['updator_stage']['replace_thesis_triplets']['prompts_version'],
        kvcache_driver_config=kvdriver_config),
    delete_obsolete_info=HYPER_PARAMS['MEM_PIPELINE_CONFIG']['updator_stage']['delete_obsolete_info']
)

# setting specific cache table for llm-task
if HYPER_PARAMS['MEM_PIPELINE_CONFIG']['llm_caching']:
    extractor_config.triplets_extraction_task_config.cache_kvdriver_config.db_config.db_info['table'] = \
        HYPER_PARAMS['MEM_PIPELINE_CONFIG']['extractor_stage']['extract_triplets']['cache_tname']
    extractor_config.thesises_extraction_task_config.cache_kvdriver_config.db_config.db_info['table'] = \
        HYPER_PARAMS['MEM_PIPELINE_CONFIG']['extractor_stage']['extract_thesises']['cache_tname']
    updator_config.replace_simple_task_config.cache_kvdriver_config.db_config.db_info['table'] = \
        HYPER_PARAMS['MEM_PIPELINE_CONFIG']['updator_stage']['replace_simple_triplets']['cache_tname']
    updator_config.replace_thesis_task_config.cache_kvdriver_config.db_config.db_info['table'] = \
        HYPER_PARAMS['MEM_PIPELINE_CONFIG']['updator_stage']['replace_thesis_triplets']['cache_tname']

# Setting Memorization Pipeline
mem_config = MemPipelineConfig(
    extractor_config=extractor_config,
    updator_config=updator_config)

mem_pipeline = MemPipeline(kg_model, mem_config)

############SAVING HYPERPARAMS############

with open(HYPER_PARAMS_PATH, 'w') as fd:
    yaml.dump(HYPER_PARAMS, fd, default_flow_style=False)

joblib.dump(gmodel_config, GRAPH_DRIVER_CONFIG_PATH)
joblib.dump(emodel_config, EMBEDDINGS_DRIVER_CONFIG_PATH)
joblib.dump(mem_config, MEM_PIPELINE_CONFIG_PATH)

########################

def diaasqa_cload(dataset_path: str) -> List[Tuple[str, Dict[str, str]]]:
    with open(dataset_path, 'r', encoding='utf-8') as fd:
        data = json.loads(fd.read())

    data_pairs = []
    for item in data['data']:
        data_pairs.append((item['text_dialog'], {'time': item['time'].split(',')[0]}))

    return data_pairs


def hotpotqa_distractor_validation_cload(dataset_path: str) -> List[Tuple[str, Dict[str, str]]]:
    contexts_df = pd.read_csv(f"{dataset_path}/relevant_contexts.csv")

    data_pair = []
    for r_idx in range(contexts_df.shape[0]):
        formated_context = f"Title: {contexts_df['title'][r_idx]}\n{contexts_df['context'][r_idx]}"
        data_pair.append((formated_context, dict()))

    return data_pair

CUSTOM_LOAD_FUNCS = {
    'diaasqa': diaasqa_cload,
    'hotpotqa_distractor_validation': hotpotqa_distractor_validation_cload
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
