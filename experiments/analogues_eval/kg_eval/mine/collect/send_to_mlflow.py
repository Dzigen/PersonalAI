print("Start logs/results collection for analysis (via mlflow)...")
import sys
import yaml
import json
import pandas as pd
from typing import Dict

import os
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://localhost:9000" # TO CHANGE
os.environ["AWS_ACCESS_KEY_ID"] = "MLFlowUser" # TO CHANGE
os.environ["AWS_SECRET_ACCESS_KEY"] = "MyFlowPass" # TO CHANGE
import mlflow

####################################################
print("1. Loading hyperparameters from .yaml files")

MLFLOW_HOST = 'localhost' # TO CHANGE
MLFLOW_PORT = 5000 # TO CHANGE
MLFLOW_EXPERIMENT_TITLE = "analogues_mine_kgeval" # TO CHANGE

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

ACCUMULATED_SCORES_SPATH = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['accumulated_scores']}"
ELAPSED_TIME_FILE_PATH = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['elapsed_time']}"
MINE_PLOT_FILE_PATH = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_SAVE_FILES']['mine_accuracy_plot']}"

MINE_CONFIG_FILE_PATH = f"{SPEC_EXPERIMENT_DIR}/mine_config" 

####################################################
print("3. Flattening dict with parameters and metrics")

def load_json(load_path: str) -> Dict:
    with open(load_path, 'r', encoding='utf-8') as fd:
        data = json.loads(fd.read())
    return data

def round5(number: float) -> float:
    return round(number, 5)

accumulated_scores = load_json(ACCUMULATED_SCORES_SPATH)
flattened_exp_scores = pd.json_normalize(accumulated_scores).to_dict(orient='records')[0]

flattened_exp_hyperp = pd.json_normalize(SPECEXP_PARAMS).to_dict(orient='records')[0]

mine_config = load_json(MINE_CONFIG_FILE_PATH)
flattened_mine_config = pd.json_normalize(mine_config).to_dict(orient='records')[0]
flattened_exp_hyperp.update(flattened_mine_config)

####################################################
print("4. Sending logs to mlflow")

MLFLOW_URI = f"http://{MLFLOW_HOST}:{MLFLOW_PORT}"
print(f"setting uri ({MLFLOW_URI})...")
mlflow.set_tracking_uri(MLFLOW_URI)

print("selecting experiment...")
mlflow.set_experiment(MLFLOW_EXPERIMENT_TITLE)

print("sending files...")
with mlflow.start_run(run_name=SPECEXP_PARAMS['EXPERIMENT_NAME']) as run_fd:
    mlflow.set_tags({
        'dataset': SPECEXP_PARAMS['DATASET_NAME'],
        'llm': SPECEXP_PARAMS['KNOWLEDGE_GRAPH_NAME'].split("_")[0], # костыль: в названии конкретного эксперимента должна содержаться информацие об использованной LLM-модели
        'knowledge_graph': SPECEXP_PARAMS['KNOWLEDGE_GRAPH_NAME'],
        'method': SPECEXP_PARAMS['METHOD_NAME']
    })

    mlflow.log_params(flattened_exp_hyperp)
    mlflow.log_metrics(flattened_exp_scores)

    # артефакты должны передаваться в mlflow-контейнер и сохраняться в volume, который к нему примонтирован.
    mlflow.log_artifact(MINE_CONFIG_FILE_PATH)
    mlflow.log_artifact(ACCUMULATED_SCORES_SPATH)
    mlflow.log_artifact(ELAPSED_TIME_FILE_PATH)
    mlflow.log_artifact(SPECEXP_PARAMS_FILEP)
    mlflow.log_artifact(MINE_PLOT_FILE_PATH)

print("############ DONE ############")
