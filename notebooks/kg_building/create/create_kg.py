print("Start Knowledge Graph creation ...")
import sys
import json
import joblib
import gc

import datetime
from tqdm import tqdm
import yaml
from pprint import pprint
import os
from typing import List, Dict, Tuple
import pandas as pd

####################################################
print("1. Loading hyperparameters from .yaml files")

KGCONN_FILE_PATH = sys.orig_argv[2]
with open(KGCONN_FILE_PATH, 'r') as stream:
    KGCONN_PARAMS = yaml.safe_load(stream)

KGENV_FILE_PATH = sys.orig_argv[3]
with open(KGENV_FILE_PATH, 'r') as stream:
    KGENV_PARAMS = yaml.safe_load(stream)

KGHYPERP_FILE_PATH = sys.orig_argv[4]
with open(KGHYPERP_FILE_PATH, 'r') as stream:
    KGHYPERP_PARAMS = yaml.safe_load(stream)

print("Loading Library...")
sys.path.insert(0, KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path'])

from src.kg_model import KnowledgeGraphModel
from src.pipelines.memorize import MemPipeline

gc.collect()

####################################################
print("2. Setting paths")

DATASET_KGS_PATH = f"{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['kg']}/{KGHYPERP_PARAMS['DATASET_NAME']}"
SPEC_KG_PATH = f"{DATASET_KGS_PATH}/{KGHYPERP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"

QA_DATASET_PATH = f"{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['qa_datasets']}/{KGHYPERP_PARAMS['DATASET_NAME']}"

TMP_EXTRACTED_TRIPLETS_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['SAVE_CONFIGS_NAMES']['tmp_extracted_triplets']}"
EXTRACTED_TRIPLETS_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['SAVE_CONFIGS_NAMES']['extracted_triplets']}"

KG_MODEL_CONFIG_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['SAVE_CONFIGS_NAMES']['kg_config']}"
MEM_PIPELINE_CONFIG_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['SAVE_CONFIGS_NAMES']['mem_pipeline_config']}"
CACHE_CONFIG_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['SAVE_CONFIGS_NAMES']['kvdriver_cache_config']}"
INFSTAT_CONFIG_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['SAVE_CONFIGS_NAMES']['inference_stat_config']}"

####################################################
print("3. Loading configs")

kgmodel_config = joblib.load(KG_MODEL_CONFIG_PATH)
mempipeline_config = joblib.load(MEM_PIPELINE_CONFIG_PATH)
kvdriver_config = joblib.load(CACHE_CONFIG_PATH)
llmstat_config = joblib.load(INFSTAT_CONFIG_PATH)

print("KG MODEL_CONFIG:\n", kgmodel_config)
print("MEM PIPELINE CONFIG: \n", mempipeline_config)
print("KVCACHE CONFIG:\n", kvdriver_config)
print("LLMSTAT CONFIG:\n", llmstat_config)

####################################################
print("4. Setting KG Model")

kg_model = KnowledgeGraphModel(kgmodel_config, kvdriver_config)

NEED_TO_CLEAR_KG = True
if NEED_TO_CLEAR_KG:
    print("Cleaning KG-model")
    kg_model.clear()

# checking knowledge graph size
pprint(kg_model.count_items(detailed=True))

####################################################
print("5. Setting Memorize Pipeline")

mem_pipeline = MemPipeline(kg_model, mempipeline_config, kvdriver_config, llmstat_config)

NEED_TO_CLEAR_CACHE = True
if NEED_TO_CLEAR_CACHE:
    print("Cleaing Mem-cache")
    mem_pipeline.clear_agent_tgen_stat()
    mem_pipeline.clear_kv_caches()

print("llmstat cache:")
pprint(mem_pipeline.get_agent_tgen_stat())
print("kv cache: ")
pprint(mem_pipeline.get_cache_stat())

####################################################
print("7. Loading dataset")

def diaasq_cload(dataset_path: str) -> List[Tuple[str, Dict[str, str]]]:
    with open(f"{dataset_path}/Augment_DiaASQ.json", 'r', encoding='utf-8') as fd:
        data = json.loads(fd.read())

    data_pairs = []
    for item in data['data']:
        data_pairs.append(
            (item['text_dialog'], item['time'].split(',')[0], dict()))

    return data_pairs


def hotpotqa_distractor_validation_cload(dataset_path: str) -> List[Tuple[str, Dict[str, str]]]:
    contexts_df = pd.read_csv(f"{dataset_path}/relevant_contexts.csv")

    data_pair = []
    for r_idx in range(contexts_df.shape[0]):
        formated_context = f"Title: {contexts_df['title'][r_idx]}\n{contexts_df['context'][r_idx]}"
        data_pair.append((formated_context, None, dict()))
    print(len(data_pair), contexts_df.shape)
    return data_pair


def triviaqa_rcwikipedia_validation_cload(dataset_path: str) -> List[Tuple[str, Dict[str, str]]]:
    contexts_df = pd.read_csv(f"{dataset_path}/relevant_contexts.csv")

    data_pair = []
    for r_idx in range(contexts_df.shape[0]):
        formated_context = f"Title: {contexts_df['title'][r_idx]}\n{contexts_df['context'][r_idx]}"
        data_pair.append((formated_context, None, dict()))

    return data_pair


CUSTOM_LOAD_FUNCS = {
    'diaasq': diaasq_cload,
    'hotpotqa_distractor_validation': hotpotqa_distractor_validation_cload,
    'trivia_qa_rcwikipedia_validation': triviaqa_rcwikipedia_validation_cload
}
dataset = CUSTOM_LOAD_FUNCS[KGHYPERP_PARAMS['DATASET_NAME']](QA_DATASET_PATH)
print(QA_DATASET_PATH)
print(len(dataset))

####################################################
print("8. Run KG build process")
print(f"start time: {datetime.datetime.now()}") 
CONSISTENCY_STEP = 100

for i in tqdm(range(len(dataset))):
    text, time, properties = dataset[i][0], dataset[i][1], dataset[i][2]
    extracted_triplets, _ = mem_pipeline.remember(text, time, properties)
    
    if i % CONSISTENCY_STEP == 0:
        kg_model.check_consistency()

    joblib.dump(extracted_triplets, f'{TMP_EXTRACTED_TRIPLETS_PATH}/item{i}')

print(f"end time: {datetime.datetime.now()}") 
kg_model.check_consistency()

print("kg size:")
pprint(kg_model.count_items(detailed=True))
print("llmstat cache:")
pprint(mem_pipeline.get_agent_tgen_stat())
print("kv cache: ")
pprint(mem_pipeline.get_cache_stat())

####################################################
print("9. Accumulating extracted triplets")

accum_triplets = []
extracted_t_files = os.listdir(TMP_EXTRACTED_TRIPLETS_PATH)
for t_file in tqdm(extracted_t_files):
    accum_triplets.append(joblib.load(
        f"{TMP_EXTRACTED_TRIPLETS_PATH}/{t_file}"))

joblib.dump(accum_triplets, EXTRACTED_TRIPLETS_PATH)

print("############ DONE ############")
