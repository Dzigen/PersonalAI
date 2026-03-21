print("Start Score-packs accumulation...")
import sys
import yaml
from collections import defaultdict
import json
from typing import Dict
import numpy as np
import os

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

####################################################
print("2. Setting paths")

EXP_RESULTS_DIR = f"{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['results']}"
EXP_KG_PATH = f"{EXP_RESULTS_DIR}/{SPECEXP_PARAMS['METHOD_NAME']}/{SPECEXP_PARAMS['DATASET_NAME']}/{SPECEXP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"
SPEC_EXPERIMENT_DIR = f"{EXP_KG_PATH}/{SPECEXP_PARAMS['EXPERIMENT_NAME']}"

BASE_METRICS_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['metrics_name']}"
LLM_METRICS_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['judges_name']}"
ELAPSED_TIME_FILE_PATH = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['elapsed_time']}"

ACCUMULATED_SCORES_SPATH = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['accumulated_scores']}"

####################################################

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

####################################################

accumulated_scores = defaultdict(list)
accumulated_base_metricnames = {
    'BLEU1': [], 'BLEU2': [], 'METEOR': [],
    'RougeL': [], 'ExactMatch': [], 'F1': [], 'NoneScore': [], 'NoAnswerScore': []#,
#    'BertScore': ['f1', 'precision', 'recall']
}

accumulated_llm_metricnames = {'llm-as-a-judge': ['mean', 'median']}

####################################################
print("3. Accumulating base scores")

base_packs = os.listdir(BASE_METRICS_DIR)
for pack_name in base_packs:
    metrics_info = load_json(f"{BASE_METRICS_DIR}/{pack_name}")

    for m_name in accumulated_base_metricnames.keys():
        if len(accumulated_base_metricnames[m_name]) == 0:
            accumulated_scores[m_name].append(metrics_info[m_name])
        else:
            for sub_m_name in accumulated_base_metricnames[m_name]:
                accumulated_scores[f"{m_name}_{sub_m_name}"].append(
                    metrics_info[m_name][sub_m_name])

####################################################
print("4. Accumulating llm-as-a-judge scores")

llm_packs = os.listdir(LLM_METRICS_DIR)
for pack_name in llm_packs:
    metrics_info = load_json(f"{LLM_METRICS_DIR}/{pack_name}")

    for m_name in accumulated_llm_metricnames.keys():
        if len(accumulated_llm_metricnames[m_name]) == 0:
            accumulated_scores[m_name].append(metrics_info[m_name])
        else:
            for sub_m_name in accumulated_llm_metricnames[m_name]:
                accumulated_scores[f"{m_name}_{sub_m_name}"].append(
                    metrics_info[m_name][sub_m_name])

####################################################

for key in accumulated_scores.keys():
    accumulated_scores[key] = round5(np.mean(accumulated_scores[key]))

####################################################
print("5. Saving accumulated scores")

times_info = load_json(ELAPSED_TIME_FILE_PATH)
for pack_name in times_info.keys():
    accumulated_scores['elapsed_time'].append(times_info[pack_name]['sum'])
accumulated_scores['elapsed_time'] = sum(accumulated_scores['elapsed_time'])

accumulated_scores = dict(accumulated_scores)
save_json(accumulated_scores,ACCUMULATED_SCORES_SPATH)

print("############ DONE ############")
