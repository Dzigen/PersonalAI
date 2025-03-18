import sys
import os
import yaml

# Read YAML file
PARAMS_FILEP = sys.orig_argv[2]
with open(PARAMS_FILEP, 'r') as stream:
    PARAMS = yaml.safe_load(stream)

DS_EXPERIMENT_DIR = f"{PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}/{PARAMS['DATASET_NAME']}"
SPEC_EXPERIMENT_DIR = f"{DS_EXPERIMENT_DIR}/{PARAMS['EXPERIMENT_NAME']}"

TMP_GENERATED_ANSWERS_DIR = f"{SPEC_EXPERIMENT_DIR}/{PARAMS['QA_EXP_DIR_STRUCT']['tmp_gen_answers_name']}"
GENERATED_ANSWERS_DIR = f"{SPEC_EXPERIMENT_DIR}/{PARAMS['QA_EXP_DIR_STRUCT']['gen_answers_name']}"
METRICS_DIR = f"{SPEC_EXPERIMENT_DIR}/{PARAMS['QA_EXP_DIR_STRUCT']['metrics_name']}"
TMP_JUDGES_DIR = f"{SPEC_EXPERIMENT_DIR}/{PARAMS['QA_EXP_DIR_STRUCT']['tmp_judges_name']}"
JUDGES_DIR = f"{SPEC_EXPERIMENT_DIR}/{PARAMS['QA_EXP_DIR_STRUCT']['judges_name']}"

if PARAMS['INIT_STRUCT']:

    print("Создаём директорию для сохранения результатов по эксперименту...")
    if not os.path.exists(DS_EXPERIMENT_DIR):
        raise ValueError(f"Директории не существует: {DS_EXPERIMENT_DIR}")

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

    os.mkdir(SPEC_EXPERIMENT_DIR)
    os.mkdir(TMP_JUDGES_DIR)
    os.mkdir(JUDGES_DIR)
    os.mkdir(TMP_GENERATED_ANSWERS_DIR)
    os.mkdir(GENERATED_ANSWERS_DIR)
    os.mkdir(METRICS_DIR)

    print("############ DONE ############")
