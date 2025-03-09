import yaml
import os
import sys

########SETTING HYPERPARAMS###########

# Read YAML file
PARAMS_FILE_PATH = sys.orig_argv[2]

with open(PARAMS_FILE_PATH, 'r') as stream:
    HYPER_PARAMS = yaml.safe_load(stream)

DATASET_PATH = f"{HYPER_PARAMS['KGS_BASE_PATH']}/{HYPER_PARAMS['DATASET_NAME']}"
KG_PATH = f"{DATASET_PATH}/{HYPER_PARAMS['KNOWLEDGE_GRAPH_NAME']}"

VECTORIZED_DB_PATH = f"{KG_PATH}/{HYPER_PARAMS['KG_DIR_STRUCT']['embeddings_dir_name']}/"
GRAPH_DB_PATH = f"{KG_PATH}/{HYPER_PARAMS['KG_DIR_STRUCT']['graph_dir_name']}/"
KV_DB_PATH = f"{KG_PATH}/{HYPER_PARAMS['KG_DIR_STRUCT']['cache_dir_name']['base']}/"
PERSISTENT_DB_PATH = KV_DB_PATH + f"{HYPER_PARAMS['KG_DIR_STRUCT']['cache_dir_name']['persistant']}/"
RAM_DB_PATH = KV_DB_PATH + f"{HYPER_PARAMS['KG_DIR_STRUCT']['cache_dir_name']['ram']}/"

TMP_EXTRACTED_TRIPLETS_PATH = f"{KG_PATH}/{HYPER_PARAMS['KG_DIR_STRUCT']['tmp_triplets_dir_name']}/"

if HYPER_PARAMS['INIT_STRUCT']:
    if not os.path.exists(HYPER_PARAMS['KGS_BASE_PATH']):
        raise ValueError(f"Директории не существует: {HYPER_PARAMS['KGS_BASE_PATH']}")
    if not os.path.exists(DATASET_PATH):
        raise ValueError(f"Директории не существует: {DATASET_PATH}")

    if os.path.exists(KG_PATH):
        raise ValueError(f"Директория существует: {KG_PATH}")
    if os.path.exists(GRAPH_DB_PATH):
        raise ValueError(f"Директория существует: {GRAPH_DB_PATH}")
    if os.path.exists(VECTORIZED_DB_PATH):
        raise ValueError(f"Директория существует: {VECTORIZED_DB_PATH}")
    if os.path.exists(KV_DB_PATH):
        raise ValueError(f"Директория существует: {KV_DB_PATH}")
    if os.path.exists(PERSISTENT_DB_PATH):
        raise ValueError(f"Директория существует: {PERSISTENT_DB_PATH}")
    if os.path.exists(RAM_DB_PATH):
        raise ValueError(f"Директория существует: {RAM_DB_PATH}")

    if os.path.exists(TMP_EXTRACTED_TRIPLETS_PATH):
        raise ValueError(f"Директория существует: {TMP_EXTRACTED_TRIPLETS_PATH}")

    os.mkdir(KG_PATH)
    os.mkdir(VECTORIZED_DB_PATH)
    os.mkdir(GRAPH_DB_PATH)
    os.mkdir(KV_DB_PATH)
    os.mkdir(PERSISTENT_DB_PATH)
    os.mkdir(RAM_DB_PATH)
    os.mkdir(TMP_EXTRACTED_TRIPLETS_PATH)
