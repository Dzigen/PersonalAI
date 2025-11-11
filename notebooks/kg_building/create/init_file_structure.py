print("Creating Knowledge Graph file structure...")
import yaml
import os
import sys

####################################################
print("1. Loading hyperparameters from .yaml files")

# Read YAML file (kgenv-file)
KGENV_FILE_PATH = sys.orig_argv[2]
with open(KGENV_FILE_PATH, 'r') as stream:
    KGENV_PARAMS = yaml.safe_load(stream)

# Read YAML file (kghyperp-file)
KGHYPERP_FILE_PATH = sys.orig_argv[3]
with open(KGHYPERP_FILE_PATH, 'r') as stream:
    KGHYPERP_PARAMS = yaml.safe_load(stream)

####################################################
print("2. Setting paths")

#
DATASET_KGS_PATH = f"{KGENV_PARAMS['BASE_PERSONALAI_PATH']}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['kg']}/{KGHYPERP_PARAMS['DATASET_NAME']}"
SPEC_KG_PATH = f"{DATASET_KGS_PATH}/{KGHYPERP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"

# embeddings-part
EMBEDDINGS_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['KG_DIR_STRUCT']['embeddings_dir']['name']}"
DENSE_EMBEDDINGS_PATH = f"{EMBEDDINGS_PATH}/{KGENV_PARAMS['KG_DIR_STRUCT']['embeddings_dir']['dense_part']}"
SPARSE_EMBEDDINGS_PATH = f"{EMBEDDINGS_PATH}/{KGENV_PARAMS['KG_DIR_STRUCT']['embeddings_dir']['sparse_part']}"

# graph-part
GRAPH_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['KG_DIR_STRUCT']['graph_dir']['name']}/{KGENV_PARAMS['KG_DIR_STRUCT']['graph_dir']['volume_name']}"

# kv-cache
CACHE_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['KG_DIR_STRUCT']['cache_dir']['name']}"
RAM_CACHE_PATH = f"{CACHE_PATH}/{KGENV_PARAMS['KG_DIR_STRUCT']['cache_dir']['ram_part']}"
PERSISTENT_CACHE_PATH = f"{CACHE_PATH}/{KGENV_PARAMS['KG_DIR_STRUCT']['cache_dir']['persistant_part']}"

# inference stat
STAT_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['KG_DIR_STRUCT']['stat_dir']['name']}/{KGENV_PARAMS['KG_DIR_STRUCT']['stat_dir']['inference']}"

SAVE_PARAMS_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['SAVE_CONFIGS_NAMES']['kg_setting']['name']}"

# tmp results
TMP_EXTRACTED_TRIPLETS_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['SAVE_CONFIGS_NAMES']['tmp_extracted_triplets']}"

####################################################
print("3. Creating directories")

if KGENV_PARAMS['INIT_STRUCT']:
    if not os.path.exists(DATASET_KGS_PATH):
        raise ValueError(f"Директории не существует: {DATASET_KGS_PATH}")

    if os.path.exists(SPEC_KG_PATH):
        raise ValueError(f"Директория существует: {SPEC_KG_PATH}")
    if os.path.exists(GRAPH_PATH):
        raise ValueError(f"Директория существует: {GRAPH_PATH}")
    if os.path.exists(DENSE_EMBEDDINGS_PATH):
        raise ValueError(f"Директория существует: {DENSE_EMBEDDINGS_PATH}")
    if os.path.exists(SPARSE_EMBEDDINGS_PATH):
        raise ValueError(f"Директория существует: {SPARSE_EMBEDDINGS_PATH}")
    if os.path.exists(RAM_CACHE_PATH):
        raise ValueError(f"Директория существует: {RAM_CACHE_PATH}")
    if os.path.exists(PERSISTENT_CACHE_PATH):
        raise ValueError(f"Директория существует: {PERSISTENT_CACHE_PATH}")
    if os.path.exists(STAT_PATH):
        raise ValueError(f"Директория существует: {STAT_PATH}")
    if os.path.exists(SAVE_PARAMS_PATH):
        raise ValueError(f"Директория существует: {SAVE_PARAMS_PATH}")

    if os.path.exists(TMP_EXTRACTED_TRIPLETS_PATH):
        raise ValueError(f"Директория существует: {TMP_EXTRACTED_TRIPLETS_PATH}")

    os.mkdir(SPEC_KG_PATH)

    os.makedirs(GRAPH_PATH, exist_ok=True)

    os.makedirs(DENSE_EMBEDDINGS_PATH, exist_ok=True)
    os.makedirs(SPARSE_EMBEDDINGS_PATH, exist_ok=True)

    os.makedirs(RAM_CACHE_PATH, exist_ok=True)
    os.makedirs(PERSISTENT_CACHE_PATH, exist_ok=True)

    os.makedirs(STAT_PATH, exist_ok=True)
    os.makedirs(SAVE_PARAMS_PATH, exist_ok=True)

    os.mkdir(TMP_EXTRACTED_TRIPLETS_PATH)

print("############ DONE ############")
