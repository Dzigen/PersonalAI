print("Start QA-pipeline inferencing...")
import sys
import yaml
import joblib
from typing import List, Tuple, Dict
from pprint import pprint
import os
import numpy as np
import pandas as pd
from time import time
from tqdm import tqdm
import json

import sys
BASE_PATH = '/home/workspace/experiments/analogues_eval' # TO CHANGE
sys.path.insert(0, BASE_PATH)

from available_methods_utils.config import AVAILABLE_GRAPHRAG_QA_METHOD, GraphRAGQAOperations
from load_dataset.qaeval_datasets import CUSTOM_LOAD_QAEVAL_FUNCS

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
SPEC_ENV_PATH = f"{CONTAINER_ENV_PATH}/{SPECEXP_PARAMS['METHOD_NAME']}/{SPECEXP_PARAMS['DATASET_NAME']}/{SPECEXP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"

# Read YAML file (kgenv-file)
KGENV_FILE_PATH = f"{SPEC_ENV_PATH}/{EXPDIR_PARAMS['KG_SETTING_DIR']['kgenv']}.yaml"
with open(KGENV_FILE_PATH, 'r') as stream:
    KGENV_PARAMS = yaml.safe_load(stream)

# Read YAML file (qaenv-file)
QAENV_FILE_PATH = f"{SPEC_ENV_PATH}/{EXPDIR_PARAMS['QAENV']}"
with open(QAENV_FILE_PATH, 'r') as stream:
    QAENV_PARAMS = yaml.safe_load(stream)

####################################################
print("2. Setting paths")

# EXP PATHS
EXPS_PATH = f"{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}"
EXP_RESULTS_DIR = f"{EXPS_PATH}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['results']}"
EXP_KG_PATH = f"{EXP_RESULTS_DIR}/{SPECEXP_PARAMS['METHOD_NAME']}/{SPECEXP_PARAMS['DATASET_NAME']}/{SPECEXP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"
SPEC_EXPERIMENT_DIR = f"{EXP_KG_PATH}/{SPECEXP_PARAMS['EXPERIMENT_NAME']}"

CONFIGS_PATH = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['configs_name']}"
QA_CONFIG_PATH = f"{CONFIGS_PATH}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['qa_config']}"

QA_DATASET_PATH = f"{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['qa_datasets']}/{SPECEXP_PARAMS['DATASET_NAME']}"

TMP_GENERATED_ANSWERS_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['tmp_gen_answers_name']}"
GENERATED_ANSWERS_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['gen_answers_name']}"

QA_ELAPSED_TIME_SPATH = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['elapsed_time']}"

# KG PATHS
DATASET_KGS_PATH = f"{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['kg']}/{SPECEXP_PARAMS['METHOD_NAME']}/{SPECEXP_PARAMS['DATASET_NAME']}"
SPEC_KG_PATH = f"{DATASET_KGS_PATH}/{SPECEXP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"

KG_MODEL_CONFIG_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['SAVE_CONFIGS_NAMES']['kg_config']}"

####################################################
print("3. Loading configs")

method_config = joblib.load(KG_MODEL_CONFIG_PATH)

####################################################
print("4. Initializing method")

method_main: GraphRAGQAOperations = AVAILABLE_GRAPHRAG_QA_METHOD[SPECEXP_PARAMS['METHOD_NAME']](method_config)
method_main.print_graph_info()

####################################################
print("5. Loading QA-dataset")

question_packs = CUSTOM_LOAD_QAEVAL_FUNCS[SPECEXP_PARAMS['DATASET_NAME']](QA_DATASET_PATH)

####################################################
print("6. Start inferencing")

for pack_name, questions, _ in question_packs:

    pack_tmp_answers_dir = f"{TMP_GENERATED_ANSWERS_DIR}/{pack_name}"
    if not os.path.exists(pack_tmp_answers_dir):
        os.mkdir(pack_tmp_answers_dir)

    process = tqdm(range(len(questions)))
    for i in process:
        process.set_postfix_str(pack_name)

        s_time = time()
        answer = method_main.perform_qa([questions[i]])[0]
        e_time = time()

        answer_dump_file = f"{pack_tmp_answers_dir}/answer_{i}"
        joblib.dump({'answer': answer, 'elapsed_time': e_time - s_time}, answer_dump_file)

####################################################
print("7. Accumulating generated answers")

elapsed_times: Dict[str,Dict[str, float]] = dict()
for pack_name, questions, gold_answers in question_packs:
    print(pack_name)

    pack_tmp_answers_dir = f"{TMP_GENERATED_ANSWERS_DIR}/{pack_name}"

    if not os.path.exists(pack_tmp_answers_dir):
        print("Папки с ответами не сущестует: ", pack_name)
        continue

    tmp_answer_dumps = os.listdir(pack_tmp_answers_dir)

    accum_answers: Dict[str,Dict[str, str]] = dict()
    elapsed_times[pack_name] = {'per_question': []}
    for tmp_dump in tqdm(tmp_answer_dumps):
        answer_info = joblib.load(f"{pack_tmp_answers_dir}/{tmp_dump}")
        answer_num = int(tmp_dump.split("_")[1])
        accum_answers[answer_num] = {
            'question': questions[answer_num],
            'gold_answer': gold_answers[answer_num],
            'gen_answer': answer_info['answer']
        }

        elapsed_times[pack_name]['per_question'].append(
            answer_info['elapsed_time'])

    elapsed_times[pack_name]['sum'] = sum(
        elapsed_times[pack_name]['per_question'])
    elapsed_times[pack_name]['mean'] = np.mean(
        elapsed_times[pack_name]['per_question'])
    elapsed_times[pack_name]['median'] = np.median(
        elapsed_times[pack_name]['per_question'])

    answers_pack_path = f"{GENERATED_ANSWERS_DIR}/{pack_name}.json"
    with open(answers_pack_path, 'w', encoding='utf-8') as fd:
        fd.write(json.dumps(accum_answers, indent=1, ensure_ascii=False))

with open(QA_ELAPSED_TIME_SPATH, 'w', encoding='utf-8') as fd:
    fd.write(json.dumps(elapsed_times, indent=1, ensure_ascii=False))

print("############ DONE ############")
