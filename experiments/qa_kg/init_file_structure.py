import sys
import os
import yaml

# Read YAML file
QA_PARAMS_FILEP = sys.orig_argv[2]
with open(QA_PARAMS_FILEP, 'r') as stream:
    QA_PARAMS = yaml.safe_load(stream)

KG_DIR_PATH = f"{QA_PARAMS['KGS_BASE_PATH']}/{QA_PARAMS['DATASET_NAME']}/{QA_PARAMS['KNOWLEDGE_GRAPH_NAME']}"
MEM_PARAMS_FILEP = f"{KG_DIR_PATH}/{QA_PARAMS['MEM_PIPELINE_HYPERP']}"
with open(MEM_PARAMS_FILEP, 'r') as stream:
    MEM_PARAMS = yaml.safe_load(stream)

GRAPH_DRIVER_CONFIG_PATH = f"{KG_DIR_PATH}/{MEM_PARAMS['SAVE_CONFIGS_NAMES']['graph_config']}"
EMBEDDINGS_DRIVER_CONFIG_PATH = f"{KG_DIR_PATH}/{MEM_PARAMS['SAVE_CONFIGS_NAMES']['embeddings_config']}"
DC_ENV_FILE_PATH = f"{KG_DIR_PATH}/{MEM_PARAMS['SAVE_CONFIGS_NAMES']['docker_compose_env']}"

DS_EXPERIMENT_DIR = f"{QA_PARAMS['EXPERIMENTS_BASE_DIR']}/{QA_PARAMS['DATASET_NAME']}"
SPEC_EXPERIMENT_DIR = f"{DS_EXPERIMENT_DIR}/{QA_PARAMS['KNOWLEDGE_GRAPH_NAME']}"

TMP_GENERATED_ANSWERS_DIR = f'{SPEC_EXPERIMENT_DIR}/{QA_PARAMS['QA_EXP_DIR_STRUCT']['tmp_gen_answers_name']}'
GENERATED_ANSWERS_DIR = f'{SPEC_EXPERIMENT_DIR}/{QA_PARAMS['QA_EXP_DIR_STRUCT']['gen_answers_name']}'
METRICS_DIR = f'{SPEC_EXPERIMENT_DIR}/{QA_PARAMS['QA_EXP_DIR_STRUCT']['metrics_name']}'

if QA_PARAMS['INIT_STRUCT']:
    print("Проверяем существование директории заданного графа знаний")
    if not os.path.exists(QA_PARAMS['KGS_BASE_PATH']):
        raise ValueError(f"Директории не существует: {QA_PARAMS['KGS_BASE_PATH']}")
    if not os.path.exists(GRAPH_DRIVER_CONFIG_PATH):
        raise ValueError(f"Файла не существует: {GRAPH_DRIVER_CONFIG_PATH}")
    if not os.path.exists(EMBEDDINGS_DRIVER_CONFIG_PATH):
        raise ValueError(f"Файла не существует: {EMBEDDINGS_DRIVER_CONFIG_PATH}")
    if not os.path.exists(DC_ENV_FILE_PATH):
        raise ValueError(f"Файла не существует: {DC_ENV_FILE_PATH}")


    if not os.path.exists(DS_EXPERIMENT_DIR):
        raise ValueError(f"Директории не существует: {DS_EXPERIMENT_DIR}")

    if not os.path.exists(SPEC_EXPERIMENT_DIR):
        raise ValueError(f"Директории существует: {SPEC_EXPERIMENT_DIR}")
    if not os.path.exists(TMP_GENERATED_ANSWERS_DIR):
        raise ValueError(f"Директории существует: {TMP_GENERATED_ANSWERS_DIR}")
    if not os.path.exists(GENERATED_ANSWERS_DIR):
        raise ValueError(f"Директории существует: {GENERATED_ANSWERS_DIR}")
    if not os.path.exists(METRICS_DIR):
        raise ValueError(f"Директории существует: {METRICS_DIR}")

    os.mkdir(SPEC_EXPERIMENT_DIR)
    os.mkdir(TMP_GENERATED_ANSWERS_DIR)
    os.mkdir(GENERATED_ANSWERS_DIR)
    os.mkdir(METRICS_DIR)
