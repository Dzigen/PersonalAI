import sys
import json
import joblib
import gc
import copy
from tqdm import tqdm
import yaml
import os
from typing import List, Dict, Tuple
import pandas as pd

# Read YAML file
PARAMS_FILE_PATH = sys.orig_argv[2]
with open(PARAMS_FILE_PATH, 'r') as stream:
    PARAMS = yaml.safe_load(stream)

sys.path.insert(0, PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path'])

from src.pipelines.memorize import MemPipeline
from src.kg_model import KnowledgeGraphModel

gc.collect()

######## SETTING HYPERPARAMS ###########

DATASET_KGS_PATH = f"{PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{PARAMS['WORKSPACE_CONTAINER_DIRS']['kg']}/{PARAMS['DATASET_NAME']}"
SPEC_KG_PATH = f"{DATASET_KGS_PATH}/{PARAMS['KNOWLEDGE_GRAPH_NAME']}"

SAVE_PARAMS_PATH = f"{SPEC_KG_PATH}/{PARAMS['SAVE_CONFIGS_NAMES']['hyperparameters']}"

TMP_EXTRACTED_TRIPLETS_PATH = f"{SPEC_KG_PATH}/{PARAMS['SAVE_CONFIGS_NAMES']['tmp_extracted_triplets']}"
EXTRACTED_TRIPLETS_PATH = f"{SPEC_KG_PATH}/{PARAMS['SAVE_CONFIGS_NAMES']['extracted_triplets']}"

GRAPH_MODEL_CONFIG_PATH = f"{SPEC_KG_PATH}/{PARAMS['SAVE_CONFIGS_NAMES']['graph_config']}"
EMBEDDINGS_MODEL_CONFIG_PATH = f"{SPEC_KG_PATH}/{PARAMS['SAVE_CONFIGS_NAMES']['embeddings_config']}"

MEM_PIPELINE_CONFIG_PATH = f"{SPEC_KG_PATH}/{PARAMS['SAVE_CONFIGS_NAMES']['mem_pipeline_config']}"
CACHE_CONFIG_PATH = f"{SPEC_KG_PATH}/{PARAMS['SAVE_CONFIGS_NAMES']['kvdriver_cache_config']}"

######## Setting knowledge graph model ######

gmodel_config = joblib.load(GRAPH_MODEL_CONFIG_PATH)
emodel_config = joblib.load(EMBEDDINGS_MODEL_CONFIG_PATH)

kg_model = KnowledgeGraphModel(
    graph_config=gmodel_config,
    embeddings_config=emodel_config)

# checking knowledge graph size
print(kg_model.embeddings_struct.vectordbs['nodes'].count_items())
print(kg_model.embeddings_struct.vectordbs['triplets'].count_items())
print(kg_model.graph_struct.db_conn.count_items())

######## SETTING MEMORIZE PIPELINE ######

mem_config = joblib.load(MEM_PIPELINE_CONFIG_PATH)
kvdriver_config =  joblib.load(CACHE_CONFIG_PATH)

mem_pipeline = MemPipeline(kg_model, mem_config, kvdriver_config)

# checking caches status
if PARAMS['MEM_PIPELINE_CONFIG']['llm_caching']:
    print("extract_triples cached: ", mem_pipeline.extractor.triplets_extraction_solver.cachekv.kv_conn.count_items())
    print("extract_thesises cached: ", mem_pipeline.extractor.thesises_extraction_solver.cachekv.kv_conn.count_items())
    print("replace_simple cached: ", mem_pipeline.updator.replace_simple_solver.cachekv.kv_conn.count_items())
    print("replace_thesises cached: ", mem_pipeline.updator.replace_hyper_solver.cachekv.kv_conn.count_items())

############ SAVING HYPERPARAMS ############

with open(SAVE_PARAMS_PATH, 'w') as fd:
    yaml.dump(PARAMS, fd, default_flow_style=False)

############ LOADING DATASET ############

def diaasqa_cload(dataset_path: str) -> List[Tuple[str, Dict[str, str]]]:
    with open(f"{dataset_path}/Augment_DiaASQ.json", 'r', encoding='utf-8') as fd:
        data = json.loads(fd.read())

    data_pairs = []
    for item in data['data']:
        data_pairs.append((item['text_dialog'], item['time'].split(',')[0], dict()))

    return data_pairs

def hotpotqa_distractor_validation_cload(dataset_path: str) -> List[Tuple[str, Dict[str, str]]]:
    contexts_df = pd.read_csv(f"{dataset_path}/relevant_contexts.csv")

    data_pair = []
    for r_idx in range(contexts_df.shape[0]):
        formated_context = f"Title: {contexts_df['title'][r_idx]}\n{contexts_df['context'][r_idx]}"
        data_pair.append((formated_context, "No time", dict()))

    return data_pair

def triviaqa_rcwikipedia_validation_cload(dataset_path: str) -> List[Tuple[str, Dict[str, str]]]:
    contexts_df = pd.read_csv(f"{dataset_path}/relevant_contexts.csv")

    data_pair = []
    for r_idx in range(contexts_df.shape[0]):
        formated_context = f"Title: {contexts_df['title'][r_idx]}\n{contexts_df['context'][r_idx]}"
        data_pair.append((formated_context, "No time", dict()))

    return data_pair

CUSTOM_LOAD_FUNCS = {
    'diaasqa': diaasqa_cload,
    'hotpotqa_distractor_validation': hotpotqa_distractor_validation_cload,
    'triviaqa_rcwikipedia_validation': triviaqa_rcwikipedia_validation_cload
}
dataset = CUSTOM_LOAD_FUNCS[PARAMS['DATASET_NAME']](PARAMS['DATASET_PATH'])
print(len(dataset))

########### KG BUILDING #############

# triviaqa 8854 of 9975

for i in tqdm(range(8854, len(dataset))):
    text, time, properties = dataset[i][0], dataset[i][1], dataset[i][2]
    extracted_triplets, _ = mem_pipeline.remember(text, time, properties)

    joblib.dump(extracted_triplets, f'{TMP_EXTRACTED_TRIPLETS_PATH}/item{i}')

########### ACCUMULATING EXTRACTED TRIPLETSs #############

accum_triplets = []
extracted_t_files = os.listdir(TMP_EXTRACTED_TRIPLETS_PATH)
for t_file in tqdm(extracted_t_files):
    accum_triplets.append(joblib.load(f"{TMP_EXTRACTED_TRIPLETS_PATH}/{t_file}"))

joblib.dump(accum_triplets, EXTRACTED_TRIPLETS_PATH)

print("############ DONE ############")
