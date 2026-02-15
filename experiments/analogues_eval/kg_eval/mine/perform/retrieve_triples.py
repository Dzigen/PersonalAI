print("Start Memory-model inferencing...")
import sys
import yaml
import joblib
from typing import List, Tuple, Dict, Set, Union
from pprint import pprint
import os
import numpy as np
from datasets import load_from_disk
import pandas as pd
from collections import Counter
from time import time
import datetime
from tqdm import tqdm
import json

import sys
BASE_PATH = '/home/workspace/experiments/analogues_eval' # TO CHANGE
sys.path.insert(0, BASE_PATH)

from available_methods_utils.config import AVAILABLE_GRAPHRAG_MINE_METHOD, GraphRAGMINEOperations
from load_dataset.kgeval_datasets import CUSTOM_LOAD_KGEVAL_DS_FUNCS

####################################################
print("1. Loading hyperparameters from .yaml files")

# Read YAML file (specexp-params)
SPECEXP_PARAMS_FILEP = sys.orig_argv[2]
with open(SPECEXP_PARAMS_FILEP, 'r') as stream:
    SPECEXP_PARAMS = yaml.safe_load(stream)

# Read YAML file (expdir-params)
EXPDIR_PARAMS_FILEP = sys.orig_argv[3]
with open(EXPDIR_PARAMS_FILEP, 'r') as stream:
    EXPDIR_PARAMS = yaml.safe_load(stream)

CONTAINER_ENV_PATH = f"{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['kg_env_path']}"
SPEC_ENV_PATH = f"{CONTAINER_ENV_PATH}/{SPECEXP_PARAMS['DATASET_NAME']}/{SPECEXP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"

# Read YAML file (kgenv-file)
KGENV_FILE_PATH = f"{SPEC_ENV_PATH}/{EXPDIR_PARAMS['KG_SETTING_DIR']['kgenv']}.yaml"
with open(KGENV_FILE_PATH, 'r') as stream:
    KGENV_PARAMS = yaml.safe_load(stream)

####################################################
print("2. Setting paths")

# EXP PATHS
EXPS_PATH = f"{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}"
EXP_RESULTS_DIR = f"{EXPS_PATH}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['results']}"
EXP_KG_PATH = f"{EXP_RESULTS_DIR}/{SPECEXP_PARAMS['METHOD_NAME']}/{SPECEXP_PARAMS['DATASET_NAME']}/{SPECEXP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"
SPEC_EXPERIMENT_DIR = f"{EXP_KG_PATH}/{SPECEXP_PARAMS['EXPERIMENT_NAME']}"

DATASET_PATH = f"{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['datasets']}/{SPECEXP_PARAMS['DATASET_NAME']}"

TMP_RETRIEVED_TRIPLES_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['tmp_retrieved_triples_name']}"
RETRIEVED_TRIPLES_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['retrieved_triples_name']}"

ELAPSED_TIME_SPATH = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['elapsed_time']}"

# KG PATHS
DATASET_KGS_PATH = f"{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['kg']}/{SPECEXP_PARAMS['METHOD_NAME']}/{SPECEXP_PARAMS['DATASET_NAME']}"
SPEC_KG_PATH = f"{DATASET_KGS_PATH}/{SPECEXP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"
KG_MODEL_CONFIG_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['SAVE_CONFIGS_NAMES']['kg_config']}"

####################################################
print("3. Loading config")

method_config = joblib.load(KG_MODEL_CONFIG_PATH)

print("KG MODEL_CONFIG:")
pprint(method_config)

####################################################
print("4. Initializing method")

method_main: GraphRAGMINEOperations = AVAILABLE_GRAPHRAG_MINE_METHOD[SPECEXP_PARAMS['METHOD_NAME']](method_config)
method_main.print_graph_info()

####################################################
print("6. Loading MINE-dataset")

queries_packs = CUSTOM_LOAD_KGEVAL_DS_FUNCS[SPECEXP_PARAMS['DATASET_NAME']](DATASET_PATH)

####################################################
print("7. Start inferencing")

print(f"start time: {datetime.datetime.now()}")
QUERIES_COUNTER = 0
for pack_name, queries in tqdm(queries_packs):

    if len(queries) < 1:
        print(f"Empty queries set; pack: {pack_name}")
        continue

    pack_tmp_triples_dir = f"{TMP_RETRIEVED_TRIPLES_DIR}/{pack_name}"
    if not os.path.exists(pack_tmp_triples_dir):
        os.mkdir(pack_tmp_triples_dir)

    for i in range(len(queries)):
        QUERIES_COUNTER += 1
        s_time = time()
        print(f"==== QUERY #{pack_name}.{i}: {queries[i]}")

        retrieved_triples: List[str] = method_main.get_neighbour_triples(queries[i])
        formated_retrieved_triples = '\n'.join(retrieved_triples)
        print(f"RETRIEVED TRIPLES IN TOTAL: {len(retrieved_triples)}\n{formated_retrieved_triples}")
        e_time = time()

        triples_dump_file = f"{pack_tmp_triples_dir}/triples_{i}"
        joblib.dump({'retrieved_triples': retrieved_triples, 'elapsed_time': e_time - s_time}, triples_dump_file)
print(f"endtime time: {datetime.datetime.now()}")

print(f"USED QUERIES IN TOTAL: {QUERIES_COUNTER}")

####################################################
print("8. Accumulating retrieved triples")

elapsed_times: Dict[str,Dict[str, float]] = dict()
for pack_name, queries in queries_packs:
    print(pack_name)

    pack_tmp_triples_dir = f"{TMP_RETRIEVED_TRIPLES_DIR}/{pack_name}"

    if not os.path.exists(pack_tmp_triples_dir):
        print("Папки с ответами не сущестует: ", pack_name)
        continue

    tmp_triples_dumps = os.listdir(pack_tmp_triples_dir)

    accum_triples: Dict[str,Dict[str, str]] = dict()
    elapsed_times[pack_name] = {'per_query': []}
    for tmp_dump in tqdm(tmp_triples_dumps):
        triples_info = joblib.load(f"{pack_tmp_triples_dir}/{tmp_dump}")
        answer_num = int(tmp_dump.split("_")[1])

        retrieved_triples: List[str] = triples_info['retrieved_triples']

        accum_triples[answer_num] = {
            'query': queries[answer_num],
            'retrieved_triples': retrieved_triples
        }

        elapsed_times[pack_name]['per_query'].append(triples_info['elapsed_time'])

    elapsed_times[pack_name]['sum'] = sum(
        elapsed_times[pack_name]['per_query'])
    elapsed_times[pack_name]['mean'] = np.mean(
        elapsed_times[pack_name]['per_query'])
    elapsed_times[pack_name]['median'] = np.median(
        elapsed_times[pack_name]['per_query'])

    answers_pack_path = f"{RETRIEVED_TRIPLES_DIR}/{pack_name}.json"
    with open(answers_pack_path, 'w', encoding='utf-8') as fd:
        fd.write(json.dumps(accum_triples, indent=1, ensure_ascii=False))

with open(ELAPSED_TIME_SPATH, 'w', encoding='utf-8') as fd:
    fd.write(json.dumps(elapsed_times, indent=1, ensure_ascii=False))

print("############ DONE ############")

kg_model.close_connections()
