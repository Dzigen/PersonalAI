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
EXP_KG_PATH = f"{EXP_RESULTS_DIR}/{SPECEXP_PARAMS['DATASET_NAME']}/{SPECEXP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"
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

groups_mapping = dict()
groups_ranges = [5, 10, 10, 10, 10, 10, 10, 10, 10, 10, 5]
cur_group = 0
cur_num = 0
for group_idx in range(len(groups_ranges)):
    for _ in range(groups_ranges[group_idx]):
        groups_mapping[cur_num] = cur_group
        cur_num += 1
    cur_group += 10

scores_groups = defaultdict(list)
for percent in percentages:
    percent_group = groups_mapping[percent]
    scores_groups[percent_group].append(percent)

cats = sorted(scores_groups.keys())
values = [len(scores_groups[cat]) for cat in cats]
w,x = 8, sorted(scores_groups.keys())

llm_model = SPECEXP_PARAMS['EXPERIMENT_NAME'].split("_")[1]

a = plt.hist(percentages, bins=12, density=False, range=[-10,110])
plt.close()
xnew = np.linspace(-5, 105, num=1000, endpoint=True)
f_cubic = interp1d(np.arange(-5,115, 10), a[0], kind='cubic')

plt.bar(x, values, w, label=f'PersonalAI, {llm_model}')

plt.plot(xnew,f_cubic(xnew), c='red', linewidth=2)
plt.vlines(x=np.mean(percentages), ymin=0, ymax=max(values), color='black', linestyle='--', linewidth=2)

plt.xticks(x, cats)
plt.xlabel('Facts captured, %')
plt.ylabel('Frequency (Articles)')
plt.legend()
plt.grid()
plt.savefig(MINE_PLOT_FILE_PATH)

print("############ DONE ############")
