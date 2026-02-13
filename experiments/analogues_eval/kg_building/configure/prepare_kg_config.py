print("Creating method config file...")
import sys
import yaml
import json

from ...available_methods_utils.config import AVAILABLE_GRAPHRAG_KGQA_METHODS

####################################################
print("1. Loading hyperparameters from .yaml files")

# Read YAML file (kg-conn)
KGCONN_FILE_PATH = sys.orig_argv[2]
with open(KGCONN_FILE_PATH, 'r') as stream:
    KGHCONN_PARAMS = yaml.safe_load(stream)

# Read YAML file (kg-env)
KGENV_FILE_PATH = sys.orig_argv[3]
with open(KGENV_FILE_PATH, 'r') as stream:
    KGENV_PARAMS = yaml.safe_load(stream)

# Read YAML file (kg-hyperp)
KGHYPERP_FILE_PATH = sys.orig_argv[4]
with open(KGHYPERP_FILE_PATH, 'r') as stream:
    KGHYPERP_PARAMS = yaml.safe_load(stream)

####################################################
print("2. Setting paths")

WORKSPACE_METHOD_KGS_PATH=f"{KGENV_PARAMS['TMP_WORKSPACE_PERSONALAI_PATH']}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['kg']}/{KGHYPERP_PARAMS['ANALOGUE_NAME']}"
WORKSPACE_SPEC_KG_PATH = f"{WORKSPACE_METHOD_KGS_PATH}/{KGHYPERP_PARAMS['DATASET_NAME']}/{KGHYPERP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"
METHOD_CONFIG_PATH = f"{WORKSPACE_SPEC_KG_PATH}/{KGENV_PARAMS['SAVE_CONFIGS_NAMES']['method_config']}"

####################################################
print("5. Setting Method Config")

custom_method_config = AVAILABLE_GRAPHRAG_KGQA_METHODS[KGHYPERP_PARAMS['ANALOGUE_NAME']].prepare_method_config(KGENV_PARAMS, KGHYPERP_PARAMS)

####################################################
print("6. Saving Method Config")

print("config: ", custom_method_config)
with open(METHOD_CONFIG_PATH, 'w', encoding='utf-8') as fd:
    fd.write(json.dumps(custom_method_config, ensure_ascii=False, indent=1))

print("############ DONE ############")
