import sys
import yaml
from collections import defaultdict
import json
from typing import Dict
import numpy as np
import os

################LOADING_HYPERPARAMETERS###################

# Read YAML file
PARAMS_FILEP = sys.orig_argv[2]
with open(PARAMS_FILEP, 'r') as stream:
    PARAMS = yaml.safe_load(stream)

DS_EXPERIMENT_DIR = f"{PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}/{PARAMS['WORKSPACE_CONTAINER_DIRS']['exp_results']}/{PARAMS['DATASET_NAME']}"
SPEC_EXPERIMENT_DIR = f"{DS_EXPERIMENT_DIR}/{PARAMS['EXPERIMENT_NAME']}"

BASE_METRICS_DIR = f"{SPEC_EXPERIMENT_DIR}/{PARAMS['QA_EXP_DIR_STRUCT']['metrics_name']}"
LLM_METRICS_DIR = f"{SPEC_EXPERIMENT_DIR}/{PARAMS['QA_EXP_DIR_STRUCT']['judges_name']}"
ELAPSED_TIME_FILE_PATH = f"{SPEC_EXPERIMENT_DIR}/{PARAMS['SAVE_CONFIGS_NAMES']['elapsed_time']}"

ACCUMULATED_SCORES_SAVE_FILE = 'accumulated_scores.json'

#################

def load_json(load_path: str) -> Dict:
    with open(load_path, 'r', encoding='utf-8') as fd:
        data = json.loads(fd.read())
    return data

def round5(number: float) -> float:
    return round(number, 5)

def save_json(data: Dict[str, object], save_path: str):
    dump = json.dumps(data, ensure_ascii=False, indent=1)
    with open(f"{save_path}", 'w', encoding='utf-8') as fd:
        fd.write(dump)

##################

accumulated_scores = defaultdict(list)
accumulated_base_meticnames = {
    'BLEU1': [], 'BLEU2': [], 'METEOR': [],
    'RougeL': [], 'ExactMatch': [], 'NoneScore': [], 'NoAnswerScore': [],
    'BertScore': ['f1', 'precision', 'recall']}

accumulated_llm_meticnames = {
    'score': ['mean', 'median']}

##################

base_packs = os.listdir(BASE_METRICS_DIR)
for pack_name in base_packs:
    metrics_info = load_json(f"{BASE_METRICS_DIR}/{pack_name}")

    for m_name in accumulated_base_meticnames.keys():
        if len(accumulated_base_meticnames[m_name]) == 0:
            accumulated_scores[m_name].append(metrics_info[m_name])
        else:
            for sub_m_name in accumulated_base_meticnames[m_name]:
                accumulated_scores[f"{m_name}_{sub_m_name}"].append(metrics_info[m_name][sub_m_name])
    
##################

llm_packs = os.listdir(LLM_METRICS_DIR)
for pack_name in llm_packs:
    metrics_info = load_json(f"{LLM_METRICS_DIR}/{pack_name}")

    for m_name in accumulated_llm_meticnames.keys():
        if len(accumulated_llm_meticnames[m_name]) == 0:
            accumulated_scores[m_name].append(metrics_info[m_name])
        else:
            for sub_m_name in accumulated_llm_meticnames[m_name]:
                accumulated_scores[f"{m_name}_{sub_m_name}"].append(metrics_info[m_name][sub_m_name])

##################

for key in accumulated_scores.keys():
    accumulated_scores[key] = round5(np.mean(accumulated_scores[key]))

##################

times_info = load_json(ELAPSED_TIME_FILE_PATH)
for pack_name in times_info.keys():
    accumulated_scores['elapsed_time'].append(times_info[pack_name]['sum'])
accumulated_scores['elapsed_time'] = sum(accumulated_scores['elapsed_time']) 

accumulated_scores = dict(accumulated_scores)
save_json(accumulated_scores, f"{SPEC_EXPERIMENT_DIR}/{ACCUMULATED_SCORES_SAVE_FILE}")