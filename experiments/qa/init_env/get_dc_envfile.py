print("Creating dotenv file for docker-compose...")
import sys
import yaml

####################################################
print("1. Loading hyperparameters from .yaml files")

# Read YAML file (qaenv-file)
QAENV_FILE_PATH = sys.orig_argv[2]
with open(QAENV_FILE_PATH, 'r') as stream:
    QAENV_PARAMS = yaml.safe_load(stream)

CONTAINER_KG_PATH = f"{QAENV_PARAMS['BASE_PERSONALAI_PATH']}/{QAENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['kg']}/{QAENV_PARAMS['DATASET_NAME']}/{QAENV_PARAMS['KNOWLEDGE_GRAPH_NAME']}"

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


SPEC_KG_PATH = f"{QAENV_PARAMS['BASE_KG_PATH']}/{QAENV_PARAMS['DATASET_NAME']}/{QAENV_PARAMS['KNOWLEDGE_GRAPH_NAME']}"

CONTAINER_EXP_PATH = f"{QAENV_PARAMS['BASE_PERSONALAI_PATH']}/{QAENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}"
SAVE_PARAMS_PATH = f"{CONTAINER_EXP_PATH}/{QAENV_PARAMS['SAVE_PARAMS_CONFIG']['base_path']}/{QAENV_PARAMS['DATASET_NAME']}/{QAENV_PARAMS['KNOWLEDGE_GRAPH_NAME']}"

####################################################
print("3. Setting dotenv variables")

# параметры для графовой бд (falkordb)
GRAPH_DB_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['KG_DIR_STRUCT']['graph_dir']['name']}/{KGENV_PARAMS['KG_DIR_STRUCT']['graph_dir']['volume_name']}"
GRAPH_CONN_PARAMS = KGCONN_PARAMS['KG_MODEL_CONNECTORS']['graph_struc_connection']
falkordb_cnt_variables = {
    'FALKORDB_CNTNAME': ADDITIONAL_DC_PARAMS['falkordb_cntname'],
    'FALKORDB_HOST': ADDITIONAL_DC_PARAMS['falkordb_host'],
    'FALKORDB_UI_EXTERNAL_PORT': ADDITIONAL_KGDC_PARAMS['falkordb_ui_port'],

    'FALKORDB_EXTERNAL_PORT': GRAPH_CONN_PARAMS['port'],

    'FALKORDB_LOCAL_VOLUME': GRAPH_DB_PATH
}

# параметры для persistent бд + llm-stat (mongo)
CACHE_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['KG_DIR_STRUCT']['cache_dir']['name']}"
PERSISTENT_CACHE_PATH = f"{CACHE_PATH}/{KGENV_PARAMS['KG_DIR_STRUCT']['cache_dir']['persistant_part']}"
PERSISTENT_CACHE_PARAMS = KGCONN_PARAMS['MEM_PIPELINE_CONNECTORS']['kv_cache_connections']['persistent_cache_config']

mongo_cnt_variables = {
    'MONGO_CNTNAME': ADDITIONAL_DC_PARAMS['mongo_cntname'],
    'MONGO_HOST': ADDITIONAL_DC_PARAMS['mongo_host'],

    'MONGO_EXTERNAL_PORT': PERSISTENT_CACHE_PARAMS['port'],
    'MONGO_AUTH_USER': PERSISTENT_CACHE_PARAMS['params']['username'],
    'MONGO_AUTH_PASS': PERSISTENT_CACHE_PARAMS['params']['password'],

    'MONGO_LOCAL_VOLUME': PERSISTENT_CACHE_PATH
}

mongoui_cnt_variables = {
    'MONGO_UI_CNTNAME': ADDITIONAL_DC_PARAMS['mongo_ui_cntname'],
    'MONGO_UI_HOST': ADDITIONAL_DC_PARAMS['mongo_ui_host'],
    'MONGO_UI_EXTERNAL_PORT': ADDITIONAL_KGDC_PARAMS['mongo_ui_port']
}

# параметры для ram бд (redis)
RAM_CACHE_PATH = f"{CACHE_PATH}/{KGENV_PARAMS['KG_DIR_STRUCT']['cache_dir']['ram_part']}"
RAM_CACHE_PARAMS = KGCONN_PARAMS['MEM_PIPELINE_CONNECTORS']['kv_cache_connections']['ram_cache_config']

redis_cnt_variables = {
    'REDIS_CNTNAME':ADDITIONAL_DC_PARAMS['redis_cntname'],
    'REDIS_HOST': ADDITIONAL_DC_PARAMS['redis_host'],

    'REDIS_EXTERNAL_PORT': RAM_CACHE_PARAMS['port'],
    'REDIS_AUTH_USER': RAM_CACHE_PARAMS['params']['username'],
    'REDIS_AUTH_PASS': RAM_CACHE_PARAMS['params']['password'],

    'REDIS_LOCAL_VOLUME': RAM_CACHE_PATH,
    'REDIS_CONFIG': f"{QAENV_PARAMS['BASE_PERSONALAI_PATH']}/{KGENV_PARAMS['PERSONALAI_REPO_DIRS']['configs']}/{ADDITIONAL_KGDC_PARAMS['redis_config_name']}"
}

redisui_cnt_variables = {
    'REDIS_UI_CNTNAME': ADDITIONAL_DC_PARAMS['redis_ui_cntname'],
    'REDIS_UI_HOST': ADDITIONAL_DC_PARAMS['redis_ui_host'],
    'REDIS_UI_EXTERNAL_PORT': ADDITIONAL_KGDC_PARAMS['redis_ui_port']
}


# параметры для qdrant бд
DENSE_DB_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['KG_DIR_STRUCT']['embeddings_dir']['name']}/{KGENV_PARAMS['KG_DIR_STRUCT']['embeddings_dir']['dense_part']}"
DENSE_CONNECTOR_PARAMS = KGCONN_PARAMS['KG_MODEL_CONNECTORS']['embeddings_struc_connection']['nodesdb_config']['dense_connector']

qdrant_cnt_variables = {
    'QDRANT_CNTNAME': ADDITIONAL_DC_PARAMS['qdrant_cntname'],
    'QDRANT_HOST': ADDITIONAL_DC_PARAMS['qdrant_host'],

    'QDRANT_EXTERNAL_PORT': DENSE_CONNECTOR_PARAMS['conn']['port'],
    'QDRANT_UI_EXTERNAL_PORT': ADDITIONAL_KGDC_PARAMS['qdrant_ui_port'],

    'QDRANT_LOCAL_VOLUME': DENSE_DB_PATH,
}

# open search
SPARSE_DB_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['KG_DIR_STRUCT']['embeddings_dir']['name']}/{KGENV_PARAMS['KG_DIR_STRUCT']['embeddings_dir']['sparse_part']}"
SPARSE_CONNECTOR_PARAMS = KGCONN_PARAMS['KG_MODEL_CONNECTORS']['embeddings_struc_connection']['nodesdb_config']['sparse_connector']

opensearch_cnt_variables = {
    'OPENSEARCH_CNTNAME': ADDITIONAL_DC_PARAMS['opensearch_cntname'],
    'OPENSEARCH_HOST': ADDITIONAL_DC_PARAMS['opensearch_host'],

    'OPENSEARCH_PORT': SPARSE_CONNECTOR_PARAMS['conn']['port'],
    'OPENSEARCH_PORT2': ADDITIONAL_KGDC_PARAMS['opensearch_port2'],

    'OPENSEARCH_LOCAL_VOLUME': SPARSE_DB_PATH,
}

# параметры для контейнера с llm-моделями
llmagents_cnt_variables = {
    'OLLAMA_CNTNAME': ADDITIONAL_DC_PARAMS['ollama_cntname'],
    'OLLAMA_HOST': ADDITIONAL_DC_PARAMS['ollama_host'],

    'OLLAMA_EXTERNAL_PORT': QAENV_PARAMS['OLLAMA_EXT_PORT'],
    'OLLAMA_DEVICE_ID': QAENV_PARAMS['GPUS_CONFIG']['ollama_device_id'],

    'OLLAMA_LOCAL_VOLUME': KGENV_PARAMS['OLLAMA_MODELS_PATH']
}

# параметры для workspace - окружения
EXT_PA_PATH = QAENV_PARAMS['BASE_PERSONALAI_PATH']
INT_PA_PATH = KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']
workspace_cnt_variables = {
    'WORKSPACE_CNTNAME': ADDITIONAL_DC_PARAMS['workspace_cntname'],
    'WORKSPACE_HOST': ADDITIONAL_DC_PARAMS['workspace_host'],
    'WORKSPACE_DEVICE_ID': QAENV_PARAMS['GPUS_CONFIG']['workspace_device_id'],

    'EXTERNAL_SPEC_KG_PATH': SPEC_KG_PATH,
    'EXTERNAL_SPEC_QADS_PATH': f"{EXT_PA_PATH}/{KGENV_PARAMS['PERSONALAI_REPO_DIRS']['qa_datasets']}/{QAENV_PARAMS['DATASET_NAME']}",
    'EXTERNAL_NOTEBOOKS_PATH': f"{EXT_PA_PATH}/{KGENV_PARAMS['PERSONALAI_REPO_DIRS']['notebooks']}",
    'EXTERNAL_EXPERIMENTS_PATH': f"{EXT_PA_PATH}/{QAENV_PARAMS['PERSONALAI_REPO_DIRS']['experiments']}",
    'EXTERNAL_SRC_PATH': f"{EXT_PA_PATH}/{KGENV_PARAMS['PERSONALAI_REPO_DIRS']['src']}",
    'EXTERNAL_MODELS_PATH': f"{KGENV_PARAMS['BASE_KG_PATH']}/../{KGENV_PARAMS['PERSONALAI_REPO_DIRS']['models']}",

    'INTERNAL_SPEC_KG_PATH': f"{INT_PA_PATH}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['kg']}/{QAENV_PARAMS['DATASET_NAME']}/{QAENV_PARAMS['KNOWLEDGE_GRAPH_NAME']}",
    'INTERNAL_SPEC_QADS_PATH': f"{INT_PA_PATH}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['qa_datasets']}/{QAENV_PARAMS['DATASET_NAME']}",
    'INTERNAL_NOTEBOOKS_PATH': f"{INT_PA_PATH}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['notebooks']}",
    'INTERNAL_EXPERIMENTS_PATH': f"{INT_PA_PATH}/{QAENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['experiments']}",
    'INTERNAL_SRC_PATH': f"{INT_PA_PATH}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['src']}",
    'INTERNAL_MODELS_PATH': f"{INT_PA_PATH}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['models']}"
}

compose_variables = {
    'COMPOSE_PROJECT_NAME': f"personalai_mmenshikov_{QAENV_PARAMS['DATASET_NAME']}_{QAENV_PARAMS['KNOWLEDGE_GRAPH_NAME']}"
}

####################################################
print("4. Formating dotenv-file")

def dictvar_to_string(dict_variables) -> str:
    return '\n'.join(list(map(lambda item: f'{item[0]}="{item[1]}"', dict_variables.items())))


def add_prefixes(dict_variables) -> None:
    for k in dict_variables.keys():
        if k.endswith("_CNTNAME"):
            dict_variables[k] = f"{dict_variables[k]}_{QAENV_PARAMS['DATASET_NAME']}_{QAENV_PARAMS['KNOWLEDGE_GRAPH_NAME']}"


env_variables = [
    falkordb_cnt_variables, qdrant_cnt_variables, mongo_cnt_variables, mongoui_cnt_variables,
    redis_cnt_variables, redisui_cnt_variables, opensearch_cnt_variables, workspace_cnt_variables]
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
