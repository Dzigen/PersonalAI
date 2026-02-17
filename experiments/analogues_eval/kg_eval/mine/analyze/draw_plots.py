print("Generaing plots for kg-quality analysis")
import sys
import yaml
import json
import numpy as np
from typing import Dict, List
from collections import defaultdict
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import os

METRICS_BASE_PATH='/home/workspace/experiments/metrics' # TO CHNAGE
sys.path.insert(0, METRICS_BASE_PATH)

from llm_as_a_judge_mine import plot_accuracy_histogram

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

LLM_METRICS_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['judges_name']}"

MINE_PLOT_FILE_PATH = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['mine_accuracy_plot']}"

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
print("2. Generating plots")

scores: List[float] = []
llm_packs = os.listdir(LLM_METRICS_DIR)
for pack_name in llm_packs:
    metrics_info = load_json(f"{LLM_METRICS_DIR}/{pack_name}")
    scores.append(metrics_info['llm-as-a-judge']['mean'])
percentages = [int(round(value * 100, 0)) for value in scores]

acc_dict = {f"{SPECEXP_PARAMS['METHOD_NAME']}, {SPECEXP_PARAMS['KNOWLEDGE_GRAPH_NAME']}": percentages}
color_map = {f"{SPECEXP_PARAMS['METHOD_NAME']}, {SPECEXP_PARAMS['KNOWLEDGE_GRAPH_NAME']}": "#a1c78f"}
plot_accuracy_histogram(acc_dict, color_map, MINE_PLOT_FILE_PATH)

print("############ DONE ############")
