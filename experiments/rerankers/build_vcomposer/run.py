print("Creating VComposer-base...")
import sys
import joblib
import yaml
import os
import json
import datetime
from time import time
import numpy as np
import pandas as pd
import hashlib
from tqdm import tqdm
from typing import List, Dict, Tuple

####################################################
print("1. Loading hyperparameters from .yaml file")

FILE_PATH = sys.orig_argv[2]
with open(FILE_PATH, 'r') as stream:
    PARAMS = yaml.safe_load(stream)


sys.path.insert(0, PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path'])

from src.db_drivers.vector_driver import VectorComposer, VectorDBConnectionConfig, VectorDriverConfig, VectorDBInstance
from src.db_drivers.vector_driver.embedders import EmbedderModel, EmbedderModelConfig

####################################################
print("2. Setting paths")

WORKSPACE_PATH = PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']
VCOMPOSER_PATH = f"{WORKSPACE_PATH}/{PARAMS['WORKSPACE_CONTAINER_DIRS']['vcomposers_data']}/{PARAMS['vcomposer_name']}"
DATASET_PATH = f"{WORKSPACE_PATH}/{PARAMS['WORKSPACE_CONTAINER_DIRS']['qa_datasets']}/{PARAMS['dataset_name']}"

PARAMS_SAVE_PATH = f"{VCOMPOSER_PATH}/{PARAMS['SAVE_CONFIGS_NAMES']['params']}"
VDB_CONFIGS_SAVE_PATH = f"{VCOMPOSER_PATH}/{PARAMS['SAVE_CONFIGS_NAMES']['vdb_configs']}"
EMBEDDER_CONFIGS_SAVE_PATH = f"{VCOMPOSER_PATH}/{PARAMS['SAVE_CONFIGS_NAMES']['embedder_configs']}"
ELAPSED_TIME_SAVE_PATH = f"{VCOMPOSER_PATH}/{PARAMS['SAVE_CONFIGS_NAMES']['elapsed_time']}"

BASE_MODELS_PATH = f"{WORKSPACE_PATH}/{PARAMS['WORKSPACE_CONTAINER_DIRS']['models']}"

####################################################
print("3. Creating VCompose directory")

CREATE_DIR = False

if CREATE_DIR:
    if os.path.exists(VCOMPOSER_PATH):
        raise ValueError(f"Директория существует: {VCOMPOSER_PATH}")
    os.mkdir(VCOMPOSER_PATH)

####################################################
print("4. Preparing configs")

#
vdb_config_mapping = dict()
for vdb_name, raw_config in PARAMS['vdb_configs'].items():
    cur_vdriver_config = VectorDriverConfig(
        db_vendor=raw_config['vendor'], vector_category=raw_config['db_category'],
        db_config=VectorDBConnectionConfig(
            db_info=raw_config['db_info'],
            params=raw_config['params'],
            conn=raw_config.get('conn', dict())
        )
    )
    vdb_config_mapping[vdb_name] = cur_vdriver_config

print(vdb_config_mapping)

#
embedder_configs_mapping = dict()
for emb_name, raw_config in PARAMS['embedder_configs'].items():
    cur_emb_confog = EmbedderModelConfig(
        model_name_or_path=f"{BASE_MODELS_PATH}/{raw_config['model_name_or_path']}",
        prompts=raw_config.get('prompts', None),
        query_prompt_name=raw_config.get('query_prompt_name', None),
        passage_prompt_name=raw_config.get('passage_prompt_name', None)
    )
    embedder_configs_mapping[emb_name] = cur_emb_confog

print(embedder_configs_mapping)

####################################################
print("5. Saving configs")

with open(PARAMS_SAVE_PATH, 'w') as fd:
    yaml.dump(PARAMS, fd, default_flow_style=False)

joblib.dump(vdb_config_mapping, VDB_CONFIGS_SAVE_PATH)

joblib.dump(embedder_configs_mapping, EMBEDDER_CONFIGS_SAVE_PATH)

####################################################
print("6. Loading embedders")

embedders_mapping = {name: EmbedderModel(config) for name, config in embedder_configs_mapping.items()}
vdb_to_embedder_mapping = {vdb_name: embedders_mapping[emb_name] for vdb_name, emb_name in PARAMS['vdb_to_embedder_mapping'].items()}

####################################################
print("7. Initing VComposer")

vcompser = VectorComposer(
    vdb_config_mapping=vdb_config_mapping,
    embedders_mapping=vdb_to_embedder_mapping
)

if PARAMS['need_clear']:
    vcompser.clear()

print(vcompser.count_items())

####################################################
print("8. Loading dataset")


def hotpotqa_distractor_validation_cload(dataset_path: str) -> List[Tuple[str, Dict[str, str]]]:
    contexts_df = pd.read_csv(f"{dataset_path}/relevant_contexts.csv")

    contexts = []
    for r_idx in range(contexts_df.shape[0]):
        formated_context = f"Title: {contexts_df['title'][r_idx]}\n{contexts_df['context'][r_idx]}"
        contexts.append((formated_context, {'cntx_idx': int(contexts_df['cntx_idx'][r_idx])}))
    print(len(contexts), contexts_df.shape)
    return contexts

def rubq_dev_cload(dataset_path: str) -> List[Tuple[str, Dict[str, str]]]:
    contexts_df = pd.read_csv(f"{dataset_path}/relevant_contexts.csv")

    contexts = []
    for r_idx in range(contexts_df.shape[0]):
        formated_context = contexts_df['context'][r_idx]
        contexts.append((formated_context, {'cntx_idx': int(contexts_df['cntx_idx'][r_idx])}))
    print(len(contexts), contexts_df.shape)
    return contexts

CUSTOM_LOAD_FUNCS = {
    'rubq_dev': rubq_dev_cload,
    'hotpotqa_distractor_validation': hotpotqa_distractor_validation_cload
}
dataset = CUSTOM_LOAD_FUNCS[PARAMS['dataset_name']](DATASET_PATH)
print(DATASET_PATH)
print(len(dataset))

####################################################
print("9. Filling VComposer")

time_stat = dict()
time_store = list()

time_stat['start_run'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"start time: {time_stat['start_run']}")
CONSISTENCY_STEP = 20
BATCH_SIZE = PARAMS['batch_size']

STEPS = None
if len(dataset) % BATCH_SIZE == 0:
    STEPS = int(len(dataset) // BATCH_SIZE)
else:
    STEPS = int(len(dataset) // BATCH_SIZE) + 1

for cur_step in tqdm(range(STEPS)):
    items = []
    for raw_item in dataset[cur_step*BATCH_SIZE:(cur_step+1)*BATCH_SIZE]:
        context, metadata = raw_item[0], raw_item[1]
        item_id = hashlib.md5(str(time()).encode()).hexdigest()
        item = VectorDBInstance(id=item_id, document=context, metadata=metadata)
        items.append(item)
    #print(items)

    s_time = time()
    vcompser.create(items)
    e_time = time()
    time_store.append(e_time - s_time)

    if cur_step % CONSISTENCY_STEP == 0:
        vcompser.check_consistency()

time_stat['end_run'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"end time: {time_stat['end_run']}")

print(vcompser.count_items())

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
print(time_stat)

vcompser.close_connection()

print("checking save storage:")
vcompser.open_connection()
print(vcompser.count_items())
del vcompser

####################################################
print("10. Saving time-statistics")

with open(ELAPSED_TIME_SAVE_PATH, 'w', encoding='utf-8') as fd:
    json.dump(time_stat, fd, indent=1, ensure_ascii=False)

print("############ DONE ############")
