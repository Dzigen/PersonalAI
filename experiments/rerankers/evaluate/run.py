print("Start exp result scoring...")
import sys
import joblib
import yaml
from pprint import pprint
import json
import datetime
import os
from time import time
import numpy as np
import ast
import pandas as pd
from tqdm import tqdm
from typing import List, Dict, Tuple
from ranx import Qrels, Run, evaluate

FILE_PATH = sys.orig_argv[2]

####################################################
print(f"1. Loading hyperparameters from .yaml file: {FILE_PATH}")

with open(FILE_PATH, 'r') as stream:
    PARAMS = yaml.safe_load(stream)

####################################################
print("2. Setting paths")

WORKSPACE_PATH = PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']
DATASET_PATH = f"{WORKSPACE_PATH}/{PARAMS['WORKSPACE_CONTAINER_DIRS']['qa_datasets']}/{PARAMS['dataset_name']}"

EXPS_BASE_PATH = f"{WORKSPACE_PATH}/{PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}"
EXPS_CATEGORY_PATH = f"{EXPS_BASE_PATH}/{PARAMS['WORKSPACE_CONTAINER_DIRS']['results_dir']}/{PARAMS['category']}"
EXP_RESULTS_PATH = f"{EXPS_CATEGORY_PATH}/{PARAMS['dataset_name']}/{PARAMS['experiment_name']}"

RETIRVED_CNTXIDS_PATH = f"{EXP_RESULTS_PATH}/{PARAMS['SAVE_CONFIGS_NAMES']['retrieved_cntx_ids']}"
SCORES_SAVE_PATH = f"{EXP_RESULTS_PATH}/{PARAMS['SAVE_CONFIGS_NAMES']['scores']}"

####################################################
print("3. Loading dataset with golden cntx_ids")

def hotpotqa_distractor_validation_qaload(dataset_path: str):
    qa_pairs_df = pd.read_csv(f"{dataset_path}/qa_pairs.csv")
    qa_pairs_df['cntx_ids'] = qa_pairs_df['cntx_ids'].map(lambda v: ast.literal_eval(v))

    qaid_cntxids_mapping = dict()
    for r_idx in range(qa_pairs_df.shape[0]):
        formated_cntx_ids = {str(cntx_idx): 1 for cntx_idx in qa_pairs_df['cntx_ids'][r_idx]}
        qaid_cntxids_mapping[str(qa_pairs_df['qa_idx'][r_idx])] = formated_cntx_ids  
    print(len(qaid_cntxids_mapping), qa_pairs_df.shape)
    return qaid_cntxids_mapping

def rubq_dev_qaload(dataset_path: str) -> List[Tuple[str, Dict[str, str]]]:
    qa_pairs_df = pd.read_csv(f"{dataset_path}/qa_pairs.csv")
    qa_pairs_df['cntx_ids'] = qa_pairs_df['cntx_ids'].map(lambda v: ast.literal_eval(v))

    qaid_cntxids_mapping = dict()
    for r_idx in range(qa_pairs_df.shape[0]):
        formated_cntx_ids = {str(cntx_idx): 1 for cntx_idx in qa_pairs_df['cntx_ids'][r_idx]}
        qaid_cntxids_mapping[str(qa_pairs_df['qa_idx'][r_idx])] = formated_cntx_ids  
    print(len(qaid_cntxids_mapping), qa_pairs_df.shape)
    return qaid_cntxids_mapping

CUSTOM_LOAD_FUNCS = {
    'rubq_dev': rubq_dev_qaload,
    'hotpotqa_distractor_validation': hotpotqa_distractor_validation_qaload
}
golden_qaidx_cntxids_mapping = CUSTOM_LOAD_FUNCS[PARAMS['dataset_name']](DATASET_PATH)
print(DATASET_PATH)
print(len(golden_qaidx_cntxids_mapping))

####################################################
print("3. Loading dataset with predicted cntx_ids")

predicted_cntxids_df = pd.read_csv(RETIRVED_CNTXIDS_PATH)
predicted_cntxids_df['retrieved_cntx_ids'] = predicted_cntxids_df['retrieved_cntx_ids'].map(lambda v: ast.literal_eval(v))

predicted_qaidx_cntxids_mapping = dict()
for r_idx in range(predicted_cntxids_df.shape[0]):
    cntxs_amount = len(predicted_cntxids_df['retrieved_cntx_ids'][r_idx])
    formated_cntx_ids = {str(cntx_idx): cntxs_amount - i for i, cntx_idx in enumerate(predicted_cntxids_df['retrieved_cntx_ids'][r_idx])}
    predicted_qaidx_cntxids_mapping[str(predicted_cntxids_df['qa_idx'][r_idx])] = formated_cntx_ids  

####################################################
print("4. Initializing metrics for results scoring")

# === Calculating ===
# 1. Precision: @10,8,5,3
# 2. Recall: @10,8,5,3
# 3. F1: @10,8,5,3
# 5. MAP: @10,8,5,3
# Used implementations: https://amenra.github.io/ranx/metrics/
# ===================

qrels = Qrels(golden_qaidx_cntxids_mapping)
run = Run(predicted_qaidx_cntxids_mapping)

####################################################
print("5. Scoring results")

BASE_METRICS = ['precision', 'recall', 'f1', 'map']
topN = ['@3', '@5', '@8', '@10']
extended_metrics = []
for metric_name in BASE_METRICS:
    extended_metrics += [metric_name + spec_top for spec_top in topN]

print("Metrics to be calculated:", extended_metrics)

scores = evaluate(qrels, run, extended_metrics)
formated_scores = {name: float(round(value,5)) for name, value in scores.items()}
pprint(formated_scores)

####################################################
print("6. Saving scores")

with open(SCORES_SAVE_PATH, 'w', encoding='utf-8') as fd:
    json.dump(formated_scores, fd, indent=1, ensure_ascii=False)