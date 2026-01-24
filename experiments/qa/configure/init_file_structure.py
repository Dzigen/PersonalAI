import sys
import os
import yaml

# Read YAML file (specexp-params)
SPECEXP_PARAMS_FILEP = sys.orig_argv[2]
with open(SPECEXP_PARAMS_FILEP, 'r') as stream:
    SPECEXP_PARAMS = yaml.safe_load(stream)

# Read YAML file (expdir-params)
EXPDIR_PARAMS_FILEP = sys.orig_argv[3]
with open(EXPDIR_PARAMS_FILEP, 'r') as stream:
    EXPDIR_PARAMS = yaml.safe_load(stream)

EXP_RESULTS_DIR = f"{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}/{EXPDIR_PARAMS['WORKSPACE_CONTAINER_DIRS']['results']}"
EXP_KG_PATH = f"{EXP_RESULTS_DIR}/{SPECEXP_PARAMS['DATASET_NAME']}/{SPECEXP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"
SPEC_EXPERIMENT_DIR = f"{EXP_KG_PATH}/{SPECEXP_PARAMS['EXPERIMENT_NAME']}"

TMP_GENERATED_ANSWERS_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['tmp_gen_answers_name']}"
GENERATED_ANSWERS_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['gen_answers_name']}"

METRICS_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['metrics_name']}"

TMP_JUDGES_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['tmp_judges_name']}"
JUDGES_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['judges_name']}"

TMP_RAGAS_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['tmp_ragas_name']}"
RAGAS_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['ragas_name']}"

QATRACE_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['qa_traces_name']}"
SETTINGS_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['settings_name']}"
CONFIGS_DIR = f"{SPEC_EXPERIMENT_DIR}/{EXPDIR_PARAMS['EXP_DIRS']['configs_name']}"

if EXPDIR_PARAMS['INIT_STRUCT']:

    print("Создаём директорию для сохранения результатов по эксперименту...")
    if not os.path.exists(EXP_KG_PATH):
        raise ValueError(f"Директории не существует: {EXP_KG_PATH}")

    if os.path.exists(SPEC_EXPERIMENT_DIR):
        raise ValueError(f"Директории существует: {SPEC_EXPERIMENT_DIR}")
    if os.path.exists(TMP_GENERATED_ANSWERS_DIR):
        raise ValueError(f"Директории существует: {TMP_GENERATED_ANSWERS_DIR}")
    if os.path.exists(GENERATED_ANSWERS_DIR):
        raise ValueError(f"Директории существует: {GENERATED_ANSWERS_DIR}")
    if os.path.exists(METRICS_DIR):
        raise ValueError(f"Директории существует: {METRICS_DIR}")
    if os.path.exists(TMP_JUDGES_DIR):
        raise ValueError(f"Директории существует: {TMP_JUDGES_DIR}")
    if os.path.exists(JUDGES_DIR):
        raise ValueError(f"Директории существует: {JUDGES_DIR}")
    if os.path.exists(SETTINGS_DIR):
        raise ValueError(f"Директории существует: {SETTINGS_DIR}")
    if os.path.exists(CONFIGS_DIR):
        raise ValueError(f"Директории существует: {CONFIGS_DIR}")

    os.mkdir(SPEC_EXPERIMENT_DIR)

    os.mkdir(TMP_JUDGES_DIR)
    os.mkdir(JUDGES_DIR)

    os.mkdir(TMP_RAGAS_DIR)
    os.mkdir(RAGAS_DIR)

    os.mkdir(TMP_GENERATED_ANSWERS_DIR)
    os.mkdir(GENERATED_ANSWERS_DIR)

    os.mkdir(QATRACE_DIR)

    os.mkdir(METRICS_DIR)
    os.mkdir(SETTINGS_DIR)
    os.mkdir(CONFIGS_DIR)

    print("############ DONE ############")
