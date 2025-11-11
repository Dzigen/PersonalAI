print("Start SingleStepReranker evaluation...")
import sys
import joblib
import yaml
from pprint import pprint
import json
import datetime
import os
from time import time
import numpy as np
import pandas as pd
from tqdm import tqdm
from typing import List, Dict, Tuple

EXP_FILE_PATH = sys.orig_argv[2]

####################################################
print(f"1. Loading hyperparameters from .yaml file: {EXP_FILE_PATH}")

with open(EXP_FILE_PATH, 'r') as stream:
    EXP_PARAMS = yaml.safe_load(stream)

sys.path.insert(0, EXP_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path'])

from src.db_drivers.vector_driver import VectorComposer, VectorDBInstance
from src.db_drivers.vector_driver.embedders import EmbedderModel
from src.rerankers.methods.SingleStepReranker import SingleStepReranker, SingleStepRerankerConfig

####################################################
print("2. Setting paths")

WORKSPACE_PATH = EXP_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']
VCOMPOSER_PATH = f"{WORKSPACE_PATH}/{EXP_PARAMS['WORKSPACE_CONTAINER_DIRS']['vcomposers_data']}/{EXP_PARAMS['vcomposer_name']}"
DATASET_PATH = f"{WORKSPACE_PATH}/{EXP_PARAMS['WORKSPACE_CONTAINER_DIRS']['qa_datasets']}/{EXP_PARAMS['dataset_name']}"

VCOMPOSER_FILE_PATH = f"{VCOMPOSER_PATH}/{EXP_PARAMS['VCOMPOSER_INFO']['params_name']}"
with open(VCOMPOSER_FILE_PATH, 'r') as stream:
    VCOMPOSER_PARAMS = yaml.safe_load(stream)

VDB_CONFIG_PATH = f"{VCOMPOSER_PATH}/{VCOMPOSER_PARAMS['SAVE_CONFIGS_NAMES']['vdb_configs']}"
EMBEDDER_CONFIG_PATH = f"{VCOMPOSER_PATH}/{VCOMPOSER_PARAMS['SAVE_CONFIGS_NAMES']['embedder_configs']}"

EXPS_BASE_PATH = f"{WORKSPACE_PATH}/{EXP_PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}"
EXPS_CATEGORY_PATH = f"{EXPS_BASE_PATH}/{EXP_PARAMS['WORKSPACE_CONTAINER_DIRS']['results_dir']}/{EXP_PARAMS['WORKSPACE_CONTAINER_DIRS']['category']}"
EXP_RESULTS_PATH = f"{EXPS_CATEGORY_PATH}/{EXP_PARAMS['dataset_name']}/{EXP_PARAMS['experiment_name']}"

ELAPSED_TIME_SAVE_PATH = f"{EXP_RESULTS_PATH}/{EXP_PARAMS['SAVE_CONFIGS_NAMES']['elapsed_time']}"
EXPPARAMS_SAVE_PATH = f"{EXP_RESULTS_PATH}/{EXP_PARAMS['SAVE_CONFIGS_NAMES']['params']}"
RERANKER_CONFIG_SAVE_PATH = f"{EXP_RESULTS_PATH}/{EXP_PARAMS['SAVE_CONFIGS_NAMES']['reranker_config']}"
RETIRVED_CNTXIDS_SAVE_PATH = f"{EXP_RESULTS_PATH}/{EXP_PARAMS['SAVE_CONFIGS_NAMES']['retrieved_cntx_ids']}"

####################################################
print("3. Creating Exp directory")

CREATE_DIR = True
if CREATE_DIR:
    if os.path.exists(EXP_RESULTS_PATH):
        raise ValueError(f"Директория существует: {EXP_RESULTS_PATH}")
    os.mkdir(EXP_RESULTS_PATH)

####################################################
print("4. Preparing Reranker config")

RAW_SINGLESTEP_CONFIG = EXP_PARAMS['singlestep_config']
reranker_config = SingleStepRerankerConfig(
    vdb_name=RAW_SINGLESTEP_CONFIG['vdb_name'],
    fetch_n=RAW_SINGLESTEP_CONFIG['fetch_n'],
    threshold=RAW_SINGLESTEP_CONFIG['threshold']
)

print("SingleStepRerankerConfig:")
pprint(reranker_config)

####################################################
print("5. Saving configs")

with open(EXPPARAMS_SAVE_PATH, 'w') as fd:
    yaml.dump(EXP_PARAMS, fd, default_flow_style=False)

joblib.dump(reranker_config, RERANKER_CONFIG_SAVE_PATH)

####################################################
print("6. Loading VComposer configs")

vdb_config_mapping = joblib.load(VDB_CONFIG_PATH)
embedder_configs_mapping = joblib.load(EMBEDDER_CONFIG_PATH)

print("vdb_config_mapping:")
pprint(vdb_config_mapping)
print("embedder_configs_mapping:")
pprint(embedder_configs_mapping)

####################################################
print("7. Initiating VComposer")

embedders_mapping = {name: EmbedderModel(config) for name, config in embedder_configs_mapping.items()}
vdb_to_embedder_mapping = {vdb_name: embedders_mapping[emb_name] for vdb_name, emb_name in VCOMPOSER_PARAMS['vdb_to_embedder_mapping'].items()}

vdb_compser = VectorComposer(
    vdb_config_mapping=vdb_config_mapping,
    embedders_mapping=vdb_to_embedder_mapping
)

print("vdb_compser:\n",vdb_compser.count_items())

####################################################
print("8. Initiating Reranker")

reranker = SingleStepReranker(
    config=reranker_config,
    vdb_composer=vdb_compser
)

####################################################
print("9. Loading dataset")

def hotpotqa_distractor_validation_qaload(dataset_path: str):
    qa_pairs_df = pd.read_csv(f"{dataset_path}/qa_pairs.csv")

    qa_pairs = []
    for r_idx in range(qa_pairs_df.shape[0]):
        qa_pairs.append(
            (qa_pairs_df['qa_idx'][r_idx], qa_pairs_df['question'][r_idx])
        )    
    print(len(qa_pairs), qa_pairs_df.shape)
    return qa_pairs

def rubq_dev_qaload(dataset_path: str) -> List[Tuple[str, Dict[str, str]]]:
    qa_pairs_df = pd.read_csv(f"{dataset_path}/qa_pairs.csv")

    qa_pairs = []
    for r_idx in range(qa_pairs_df.shape[0]):
        qa_pairs.append(
            (qa_pairs_df['qa_idx'][r_idx], qa_pairs_df['question'][r_idx])
        )    
    print(len(qa_pairs), qa_pairs_df.shape)
    return qa_pairs

CUSTOM_LOAD_FUNCS = {
    'rubq_dev': rubq_dev_qaload,
    'hotpotqa_distractor_validation': hotpotqa_distractor_validation_qaload
}
dataset = CUSTOM_LOAD_FUNCS[EXP_PARAMS['dataset_name']](DATASET_PATH)
print(DATASET_PATH)
print(len(dataset))

####################################################
print("10. Evaluating Reranker")

time_stat = dict()
time_store = list()

time_stat['start_run'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"start time: {time_stat['start_run']}")

retrieved_cntx_ids = list()
#for i in tqdm(range(10)):
for i in tqdm(range(len(dataset))):
    qa_idx, question = dataset[i][0], dataset[i][1]
   
    s_time = time()
    retrieved_items: List[VectorDBInstance] = reranker.run(
        query=question, top_k=EXP_PARAMS['top_k'],
        subset_ids=None, includes=['metadatas'],
        return_with_embeddings=False,
        return_with_scores=False
    )
    e_time = time()
    time_store.append(e_time - s_time)

    formated_cntx_ids = list(map(lambda item: item.metadata['cntx_idx'], retrieved_items))
    retrieved_cntx_ids.append((qa_idx, formated_cntx_ids))
    
time_stat['end_run'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"end time: {time_stat['end_run']}")

print("vdb_compser:\n",vdb_compser.count_items())

time_stat['detailed(sec)'] = {
    'count': len(time_store),
    'sum': round(sum(time_store), 3),
    'mean': float(round(np.mean(time_store), 3)),
    'median': float(round(np.median(time_store), 3)),
    'std': float(round(np.std(time_store), 3)),
    'min': float(round(np.min(time_store), 3)),
    'max': float(round(np.max(time_store), 3))
}

print("time stat:")
pprint(time_stat)

####################################################
print("11. Saving Results")

with open(ELAPSED_TIME_SAVE_PATH, 'w', encoding='utf-8') as fd:
    json.dump(time_stat, fd, indent=1, ensure_ascii=False)

retrievedcntxids_df = pd.DataFrame(retrieved_cntx_ids, columns=['qa_idx', 'retrieved_cntx_ids'])
retrievedcntxids_df.to_csv(RETIRVED_CNTXIDS_SAVE_PATH, index=False)

print("############ DONE ############")