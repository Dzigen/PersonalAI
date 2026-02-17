print("Creating dotenv file for docker-compose...")
import sys
import yaml

from ...available_methods_utils.config import AVAILABLE_GRAPHRAG_BUILD_METHODS

####################################################
print("1. Loading hyperparameters from .yaml files")

# Read YAML file (kgconn-file)
KGCONN_FILE_PATH = sys.orig_argv[2]
with open(KGCONN_FILE_PATH, 'r') as stream:
    KGCONN_PARAMS = yaml.safe_load(stream)

# Read YAML file (kgenv-file)
KGENV_FILE_PATH = sys.orig_argv[3]
with open(KGENV_FILE_PATH, 'r') as stream:
    KGENV_PARAMS = yaml.safe_load(stream)

# Read YAML file (kghyperp-file)
KGHYPERP_FILE_PATH = sys.orig_argv[4]
with open(KGHYPERP_FILE_PATH, 'r') as stream:
    KGHYPERP_PARAMS = yaml.safe_load(stream)

####################################################
print("2. Setting paths")

#
ADDITIONAL_DC_PARAMS = KGCONN_PARAMS['CONTAINERS_ADDITIONAL_CONFIG']

LOCAL_METHOD_KGS_PATH=f"{KGENV_PARAMS['LOCAL_KG_PATH']}/{KGHYPERP_PARAMS['ANALOGUE_NAME']}"
LOCAL_SPEC_KG_PATH = f"{LOCAL_METHOD_KGS_PATH}/{KGHYPERP_PARAMS['DATASET_NAME']}/{KGHYPERP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"

TMP_METHODS_KGS_PATH=f"{KGENV_PARAMS['TMP_WORKSPACE_PERSONALAI_PATH']}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['kg']}/{KGHYPERP_PARAMS['ANALOGUE_NAME']}"
TMP_SPEC_KG_PATH = f"{TMP_METHODS_KGS_PATH}/{KGHYPERP_PARAMS['DATASET_NAME']}/{KGHYPERP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"

SAVE_PARAMS_PATH = f"{TMP_SPEC_KG_PATH}/{KGENV_PARAMS['SAVE_CONFIGS_NAMES']['kg_setting']['name']}"

CONTAINERS_NAME_POSTFIX=f"{KGHYPERP_PARAMS['ANALOGUE_NAME']}_{KGHYPERP_PARAMS['DATASET_NAME']}_{KGHYPERP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"

####################################################
print("3. Setting dotenv variables")

# параметры для контейнера с llm-моделями
llmagents_cnt_variables = {
    'OLLAMA_CNTNAME': ADDITIONAL_DC_PARAMS['ollama_cntname'],
    'OLLAMA_HOST': ADDITIONAL_DC_PARAMS['ollama_host'],

    'OLLAMA_EXTERNAL_PORT': KGHYPERP_PARAMS['KG_CONFIG']['agent_configs']['default']['ext_params'].get('port', 11437),
    'OLLAMA_DEVICE_ID': KGCONN_PARAMS['GPUS_CONFIG']['ollama_device_id'],

    'OLLAMA_LOCAL_VOLUME': KGENV_PARAMS['OLLAMA_MODELS_PATH']
}

# параметры для workspace - окружения
EXT_PA_PATH = KGENV_PARAMS['BASE_PERSONALAI_PATH']
INT_PA_PATH = KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']
workspace_cnt_variables = {
    'WORKSPACE_CNTNAME': ADDITIONAL_DC_PARAMS['workspace_cntname'],
    'WORKSPACE_HOST': ADDITIONAL_DC_PARAMS['workspace_host'],
    'WORKSPACE_DEVICE_ID': KGCONN_PARAMS['GPUS_CONFIG']['workspace_device_id'],

    'EXTERNAL_SPEC_KG_PATH': LOCAL_SPEC_KG_PATH,
    'EXTERNAL_SPEC_DS_PATH': f"{EXT_PA_PATH}/{KGENV_PARAMS['PERSONALAI_REPO_DIRS']['datasets']}/{KGHYPERP_PARAMS['DATASET_NAME']}",
    'EXTERNAL_NOTEBOOKS_PATH': f"{EXT_PA_PATH}/{KGENV_PARAMS['PERSONALAI_REPO_DIRS']['notebooks']}",
    'EXTERNAL_EXPERIMENTS_PATH': f"{EXT_PA_PATH}/{KGENV_PARAMS['PERSONALAI_REPO_DIRS']['experiments']}",
    'EXTERNAL_SRC_PATH': f"{EXT_PA_PATH}/{KGENV_PARAMS['PERSONALAI_REPO_DIRS']['src']}",
    'EXTERNAL_MODELS_PATH': f"{KGENV_PARAMS['BASE_KG_PATH']}/../{KGENV_PARAMS['PERSONALAI_REPO_DIRS']['models']}",

    'INTERNAL_SPEC_KG_PATH': f"{INT_PA_PATH}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['kg']}/{KGHYPERP_PARAMS['DATASET_NAME']}/{KGHYPERP_PARAMS['KNOWLEDGE_GRAPH_NAME']}",
    'INTERNAL_SPEC_DS_PATH': f"{INT_PA_PATH}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['datasets']}/{KGHYPERP_PARAMS['DATASET_NAME']}",
    'INTERNAL_NOTEBOOKS_PATH': f"{INT_PA_PATH}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['notebooks']}",
    'INTERNAL_EXPERIMENTS_PATH': f"{INT_PA_PATH}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}",
    'INTERNAL_SRC_PATH': f"{INT_PA_PATH}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['src']}",
    'INTERNAL_MODELS_PATH': f"{INT_PA_PATH}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['models']}"
}

compose_variables = {
    'COMPOSE_PROJECT_NAME': f"personalai_mmenshikov_{CONTAINERS_NAME_POSTFIX}"
}

method_custom_env_variables = AVAILABLE_GRAPHRAG_BUILD_METHODS[KGHYPERP_PARAMS['ANALOGUE_NAME']].prepare_kgbuild_env_params(KGCONN_PARAMS, KGHYPERP_PARAMS)

####################################################
print("4. Formating dotenv-file")

def dictvar_to_string(dict_variables) -> str:
    return '\n'.join(list(map(lambda item: f'{item[0]}="{item[1]}"', dict_variables.items())))

def add_prefixes(dict_variables) -> None:
    for k in dict_variables.keys():
        if k.endswith("_CNTNAME"):
            dict_variables[k] = f"{dict_variables[k]}_{CONTAINERS_NAME_POSTFIX}"

env_variables = method_custom_env_variables + [workspace_cnt_variables]
for variables in env_variables:
    add_prefixes(variables)
env_variables += [llmagents_cnt_variables, compose_variables]

env_variables = '\n'.join(
    list(map(lambda vars: dictvar_to_string(vars), env_variables)))

####################################################
print("5. Saving dotenv-file")

DC_ENV_PATH = f"{TMP_SPEC_KG_PATH}/{KGENV_PARAMS['SAVE_CONFIGS_NAMES']['docker_compose_env']}"
with open(DC_ENV_PATH, 'w', encoding='utf-8') as fd:
    fd.write(env_variables)

####################################################
print("6. Saving Used .yaml files")

SAVE_PARAMS_CONFIG = KGENV_PARAMS['SAVE_CONFIGS_NAMES']['kg_setting']

with open(f"{SAVE_PARAMS_PATH}/{SAVE_PARAMS_CONFIG['kgconn']}.yaml", 'w') as fd:
    yaml.dump(KGCONN_PARAMS, fd, default_flow_style=False, sort_keys=False)
with open(f"{SAVE_PARAMS_PATH}/{SAVE_PARAMS_CONFIG['kgenv']}.yaml", 'w') as fd:
    yaml.dump(KGENV_PARAMS, fd, default_flow_style=False, sort_keys=False)
with open(f"{SAVE_PARAMS_PATH}/{SAVE_PARAMS_CONFIG['kghyperp']}.yaml", 'w') as fd:
    yaml.dump(KGHYPERP_PARAMS, fd, default_flow_style=False, sort_keys=False)

print("############ DONE ############")
