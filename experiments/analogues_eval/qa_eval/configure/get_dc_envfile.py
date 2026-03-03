print("Creating dotenv file for docker-compose...")
import sys
import yaml
import os

EXPERIMETS_BASE_PATH="/home/m.menschikov/workspace/personal_ai/Personal-AI/experiments" # TO CHANGE
sys.path.insert(0, EXPERIMETS_BASE_PATH)
from analogues_eval.available_methods_utils.config import AVAILABLE_GRAPHRAG_QA_METHOD

####################################################
print("1. Loading hyperparameters from .yaml files")

# Read YAML file (qaenv-file)
QAEVAL_FILE_PATH = sys.orig_argv[2]
with open(QAEVAL_FILE_PATH, 'r') as stream:
    QAENV_PARAMS = yaml.safe_load(stream)

SPEC_ENV_RELPATH = f"{QAENV_PARAMS['METHOD_NAME']}/{QAENV_PARAMS['DATASET_NAME']}/{QAENV_PARAMS['KNOWLEDGE_GRAPH_NAME']}"
CONTAINER_KG_PATH = f"{QAENV_PARAMS['LOCAL_PERSONALAI_PATH']}/{QAENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['kg']}/{SPEC_ENV_RELPATH}"

# Read YAML file (kgenv-file)
KGENV_FILE_PATH = f"{CONTAINER_KG_PATH}/{QAENV_PARAMS['KG_SETTING_DIR']['name']}/{QAENV_PARAMS['KG_SETTING_DIR']['kgenv']}.yaml"
with open(KGENV_FILE_PATH, 'r') as stream:
    KGENV_PARAMS = yaml.safe_load(stream)

# Read YAML file (kgconn-file)
KGCONN_FILE_PATH = f"{CONTAINER_KG_PATH}/{QAENV_PARAMS['KG_SETTING_DIR']['name']}/{QAENV_PARAMS['KG_SETTING_DIR']['kgconn']}.yaml"
with open(KGCONN_FILE_PATH, 'r') as stream:
    KGCONN_PARAMS = yaml.safe_load(stream)

####################################################
print("2. Setting paths")

#
ADDITIONAL_DC_PARAMS = QAENV_PARAMS['CONTAINERS_ADDITIONAL_CONFIG']
ADDITIONAL_KGDC_PARAMS = KGCONN_PARAMS['CONTAINERS_ADDITIONAL_CONFIG']
SPEC_KG_PATH = f"{QAENV_PARAMS['LOCAL_KG_PATH']}/{SPEC_ENV_RELPATH}"

CONTAINER_EXP_PATH = f"{QAENV_PARAMS['LOCAL_PERSONALAI_PATH']}/{QAENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}/analogues_eval/qa_eval"
SAVE_PARAMS_PATH = f"{CONTAINER_EXP_PATH}/{QAENV_PARAMS['SAVE_PARAMS_CONFIG']['base_path']}/{SPEC_ENV_RELPATH}"

if os.path.exists(SAVE_PARAMS_PATH):
    print(f"Директория существует: {SAVE_PARAMS_PATH}")
else:
    os.mkdir(SAVE_PARAMS_PATH)

####################################################
print("3. Setting dotenv variables")

custom_env_variables = AVAILABLE_GRAPHRAG_QA_METHOD[QAENV_PARAMS['METHOD_NAME']].prepare_qaeval_env_params(KGCONN_PARAMS, QAENV_PARAMS)

# параметры для контейнера с llm-моделями
llmagents_cnt_variables = {
    'OLLAMA_CNTNAME': ADDITIONAL_DC_PARAMS['ollama_cntname'],
    'OLLAMA_HOST': ADDITIONAL_DC_PARAMS['ollama_host'],

    'OLLAMA_EXTERNAL_PORT': QAENV_PARAMS['OLLAMA_EXT_PORT'],
    'OLLAMA_DEVICE_ID': QAENV_PARAMS['GPUS_CONFIG']['ollama_device_id'],

    'OLLAMA_LOCAL_VOLUME': KGENV_PARAMS['OLLAMA_MODELS_PATH']
}

# параметры для workspace - окружения
EXT_PA_PATH = QAENV_PARAMS['LOCAL_PERSONALAI_PATH']
INT_PA_PATH = KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']
workspace_cnt_variables = {
    'WORKSPACE_CNTNAME': ADDITIONAL_DC_PARAMS['workspace_cntname'],
    'WORKSPACE_HOST': ADDITIONAL_DC_PARAMS['workspace_host'],
    'WORKSPACE_DEVICE_ID': QAENV_PARAMS['GPUS_CONFIG']['workspace_device_id'],

    'EXTERNAL_SPEC_KG_PATH': SPEC_KG_PATH,
    'EXTERNAL_SPEC_DS_PATH': f"{EXT_PA_PATH}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['datasets']}/{QAENV_PARAMS['DATASET_NAME']}",
    'EXTERNAL_NOTEBOOKS_PATH': f"{EXT_PA_PATH}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['notebooks']}",
    'EXTERNAL_EXPERIMENTS_PATH': f"{EXT_PA_PATH}/{QAENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}",
    'EXTERNAL_SRC_PATH': f"{EXT_PA_PATH}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['src']}",
    'EXTERNAL_MODELS_PATH': f"{KGENV_PARAMS['LOCAL_KG_PATH']}/../../{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['models']}",

    'INTERNAL_SPEC_KG_PATH': f"{INT_PA_PATH}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['kg']}/{QAENV_PARAMS['METHOD_NAME']}/{QAENV_PARAMS['DATASET_NAME']}/{QAENV_PARAMS['KNOWLEDGE_GRAPH_NAME']}",
    'INTERNAL_SPEC_DS_PATH': f"{INT_PA_PATH}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['datasets']}/{QAENV_PARAMS['DATASET_NAME']}",
    'INTERNAL_NOTEBOOKS_PATH': f"{INT_PA_PATH}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['notebooks']}",
    'INTERNAL_EXPERIMENTS_PATH': f"{INT_PA_PATH}/{QAENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}",
    'INTERNAL_SRC_PATH': f"{INT_PA_PATH}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['src']}",
    'INTERNAL_MODELS_PATH': f"{INT_PA_PATH}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['models']}"
}

compose_variables = {
    'COMPOSE_PROJECT_NAME': f"personalai_mmenshikov_{QAENV_PARAMS['METHOD_NAME']}_{QAENV_PARAMS['DATASET_NAME']}_{QAENV_PARAMS['KNOWLEDGE_GRAPH_NAME']}"
}

####################################################
print("4. Formating dotenv-file")

def dictvar_to_string(dict_variables) -> str:
    return '\n'.join(list(map(lambda item: f'{item[0]}="{item[1]}"', dict_variables.items())))


def add_prefixes(dict_variables) -> None:
    for k in dict_variables.keys():
        if k.endswith("_CNTNAME"):
            dict_variables[k] = f"{dict_variables[k]}_{QAENV_PARAMS['METHOD_NAME']}_{QAENV_PARAMS['DATASET_NAME']}_{QAENV_PARAMS['KNOWLEDGE_GRAPH_NAME']}"


env_variables = [workspace_cnt_variables]
for variables in env_variables:
    add_prefixes(variables)
env_variables += [llmagents_cnt_variables, compose_variables]

env_variables = '\n'.join(
    list(map(lambda vars: dictvar_to_string(vars), env_variables)))

####################################################
print("5. Saving dotenv-file")

DC_ENV_PATH = f"{SAVE_PARAMS_PATH}/{QAENV_PARAMS['SAVE_PARAMS_CONFIG']['env_file']}"
with open(DC_ENV_PATH, 'w', encoding='utf-8') as fd:
    fd.write(env_variables)

####################################################
print("6. Saving Used .yaml files")

SAVE_PARAMS_CONFIG = QAENV_PARAMS['SAVE_PARAMS_CONFIG']

with open(f"{SAVE_PARAMS_PATH}/{SAVE_PARAMS_CONFIG['kgconn']}", 'w') as fd:
    yaml.dump(KGCONN_PARAMS, fd, default_flow_style=False, sort_keys=False)
with open(f"{SAVE_PARAMS_PATH}/{SAVE_PARAMS_CONFIG['kgenv']}", 'w') as fd:
    yaml.dump(KGENV_PARAMS, fd, default_flow_style=False, sort_keys=False)
with open(f"{SAVE_PARAMS_PATH}/{SAVE_PARAMS_CONFIG['qaenv']}", 'w') as fd:
    yaml.dump(QAENV_PARAMS, fd, default_flow_style=False, sort_keys=False)

print("############ DONE ############")
