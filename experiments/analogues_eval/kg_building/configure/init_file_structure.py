print("Creating Knowledge Graph file structure...")
import yaml
import os
import sys

EXPERIMETS_BASE_PATH="/home/m.menschikov/workspace/personal_ai/Personal-AI/experiments" # TO CHANGE
sys.path.insert(0, EXPERIMETS_BASE_PATH)
from analogues_eval.available_methods_utils.config import AVAILABLE_GRAPHRAG_BUILD_METHODS

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
ANALOGUES_KGS_BASE_PATH = f"{KGENV_PARAMS['TMP_WORKSPACE_PERSONALAI_PATH']}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['kg']}/{KGHYPERP_PARAMS['METHOD_NAME']}"
DATASET_KGS_PATH = f"{ANALOGUES_KGS_BASE_PATH}/{KGHYPERP_PARAMS['DATASET_NAME']}"
SPEC_KG_PATH = f"{DATASET_KGS_PATH}/{KGHYPERP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"

SAVE_PARAMS_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['SAVE_CONFIGS_NAMES']['kg_setting']['name']}"

####################################################
print("3. Creating directories")

if not os.path.exists(DATASET_KGS_PATH):
    raise ValueError(f"Директории не существует: {DATASET_KGS_PATH}")

if os.path.exists(SPEC_KG_PATH):
    raise ValueError(f"Директория существует: {SPEC_KG_PATH}")
if os.path.exists(SAVE_PARAMS_PATH):
    raise ValueError(f"Директория существует: {SAVE_PARAMS_PATH}")

os.mkdir(SPEC_KG_PATH)

os.makedirs(SAVE_PARAMS_PATH, exist_ok=True)

AVAILABLE_GRAPHRAG_BUILD_METHODS[KGHYPERP_PARAMS['METHOD_NAME']].create_kg_structure(KGENV_PARAMS, KGHYPERP_PARAMS)

print("############ DONE ############")
