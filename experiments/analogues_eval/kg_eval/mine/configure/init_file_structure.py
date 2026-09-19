import sys
import os
import yaml

####################################################

# Read YAML file (specexp-params)
SPECEXP_PARAMS_FILEP = sys.orig_argv[2]
with open(SPECEXP_PARAMS_FILEP, 'r') as stream:
    SPECEXP_PARAMS = yaml.safe_load(stream)

# Read YAML file (expdir-params)
EXPDIR_PARAMS_FILEP = sys.orig_argv[3]
with open(EXPDIR_PARAMS_FILEP, 'r') as stream:
    EXPDIR_PARAMS = yaml.safe_load(stream)

####################################################

EXP_RESULTS_DIR = f"{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['results']}"
EXP_KG_PATH = f"{EXP_RESULTS_DIR}/{SPECEXP_PARAMS['METHOD_NAME']}/{SPECEXP_PARAMS['DATASET_NAME']}/{SPECEXP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"
SPEC_EXPERIMENT_DIR = f"{EXP_KG_PATH}/{SPECEXP_PARAMS['EXPERIMENT_NAME']}"

TMP_RETRIEVED_TRIPLES_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['tmp_retrieved_triples_name']}"
RETRIEVED_TRIPLES_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['retrieved_triples_name']}"

METRICS_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['metrics_name']}"

TMP_JUDGES_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['tmp_judges_name']}"
JUDGES_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['judges_name']}"

SETTINGS_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['settings_name']}"

SPECEXP_PARAMS_SPATH = f"{SETTINGS_DIR }/{EXPDIR_PARAMS['EXP_SAVE_FILES']['kghyperp']}"
EXPDIR_PARAMS_SPATH = f"{SETTINGS_DIR }/{EXPDIR_PARAMS['EXP_SAVE_FILES']['expdir']}"

####################################################
print("1. Creating exp-folder")

if EXPDIR_PARAMS['INIT_STRUCT']:

    print("Создаём директорию для сохранения результатов по эксперименту...")
    if not os.path.exists(EXP_KG_PATH):
        raise ValueError(f"Директории не существует: {EXP_KG_PATH}")

    if os.path.exists(SPEC_EXPERIMENT_DIR):
        raise ValueError(f"Директории существует: {SPEC_EXPERIMENT_DIR}")
    if os.path.exists(TMP_RETRIEVED_TRIPLES_DIR):
        raise ValueError(f"Директории существует: {TMP_RETRIEVED_TRIPLES_DIR}")
    if os.path.exists(RETRIEVED_TRIPLES_DIR):
        raise ValueError(f"Директории существует: {RETRIEVED_TRIPLES_DIR}")
    if os.path.exists(METRICS_DIR):
        raise ValueError(f"Директории существует: {METRICS_DIR}")
    if os.path.exists(TMP_JUDGES_DIR):
        raise ValueError(f"Директории существует: {TMP_JUDGES_DIR}")
    if os.path.exists(JUDGES_DIR):
        raise ValueError(f"Директории существует: {JUDGES_DIR}")
    if os.path.exists(SETTINGS_DIR):
        raise ValueError(f"Директории существует: {SETTINGS_DIR}")

    os.mkdir(SPEC_EXPERIMENT_DIR)

    os.mkdir(TMP_JUDGES_DIR)
    os.mkdir(JUDGES_DIR)

    os.mkdir(TMP_RETRIEVED_TRIPLES_DIR)
    os.mkdir(RETRIEVED_TRIPLES_DIR)

    os.mkdir(METRICS_DIR)
    os.mkdir(SETTINGS_DIR)

####################################################
print("2. Saving params")

with open(SPECEXP_PARAMS_SPATH, 'w') as fd:
    yaml.dump(SPECEXP_PARAMS, fd, default_flow_style=False, sort_keys=False)

with open(EXPDIR_PARAMS_SPATH, 'w') as fd:
    yaml.dump(EXPDIR_PARAMS, fd, default_flow_style=False, sort_keys=False)

print("############ DONE ############")
