print("Creating dotenv file for docker-compose...")
import sys
import yaml

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


DATASET_KGS_PATH = f"{KGENV_PARAMS['BASE_KG_PATH']}/{KGHYPERP_PARAMS['DATASET_NAME']}"
SPEC_KG_PATH = f"{DATASET_KGS_PATH}/{KGHYPERP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"


CONTAINER_KG_PATH = f"{KGENV_PARAMS['BASE_PERSONALAI_PATH']}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['kg']}/{KGHYPERP_PARAMS['DATASET_NAME']}/{KGHYPERP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"
SAVE_PARAMS_PATH = f"{CONTAINER_KG_PATH}/{KGENV_PARAMS['SAVE_CONFIGS_NAMES']['kg_setting']['name']}"

####################################################
print("3. Setting dotenv variables")

# параметры для графовой бд (neo4j)
GRAPH_DB_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['KG_DIR_STRUCT']['graph_dir']['name']}/{KGENV_PARAMS['KG_DIR_STRUCT']['graph_dir']['volume_name']}"
GRAPH_CONN_PARAMS = KGCONN_PARAMS['KG_MODEL_CONNECTORS']['graph_struc_connection']
neo4j_cnt_variables = {
    'NEO4J_CNTNAME': ADDITIONAL_DC_PARAMS['neo4j_cntname'],
    'NEO4J_HOST': ADDITIONAL_DC_PARAMS['neo4j_host'],
    'NEO4J_UI_EXTERNAL_PORT': ADDITIONAL_DC_PARAMS['neo4j_ui_port'],

    'NEO4J_EXTERNAL_PORT': GRAPH_CONN_PARAMS['port'],
    'NEO4j_AUTH_USER': GRAPH_CONN_PARAMS['params']['user'],
    'NEO4j_AUTH_PWD': GRAPH_CONN_PARAMS['params']['pwd'],

    'NEO4J_LOCAL_VOLUME': GRAPH_DB_PATH
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
    'MONGO_UI_EXTERNAL_PORT': ADDITIONAL_DC_PARAMS['mongo_ui_port']
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
    'REDIS_CONFIG': f"{KGENV_PARAMS['BASE_PERSONALAI_PATH']}/{KGENV_PARAMS['PERSONALAI_REPO_DIRS']['configs']}/{ADDITIONAL_DC_PARAMS['redis_config_name']}"
}

redisui_cnt_variables = {
    'REDIS_UI_CNTNAME': ADDITIONAL_DC_PARAMS['redis_ui_cntname'],
    'REDIS_UI_HOST': ADDITIONAL_DC_PARAMS['redis_ui_host'],
    'REDIS_UI_EXTERNAL_PORT': ADDITIONAL_DC_PARAMS['redis_ui_port']
}


# параметры для qdrant бд
DENSE_DB_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['KG_DIR_STRUCT']['embeddings_dir']['name']}/{KGENV_PARAMS['KG_DIR_STRUCT']['embeddings_dir']['dense_part']}"
DENSE_CONNECTOR_PARAMS = KGCONN_PARAMS['KG_MODEL_CONNECTORS']['embeddings_struc_connection']['nodesdb_config']['dense_connector']

qdrant_cnt_variables = {
    'QDRANT_CNTNAME': ADDITIONAL_DC_PARAMS['qdrant_cntname'],
    'QDRANT_HOST': ADDITIONAL_DC_PARAMS['qdrant_host'],

    'QDRANT_EXTERNAL_PORT1': DENSE_CONNECTOR_PARAMS['conn']['port'],
    'QDRANT_UI_EXTERNAL_PORT': ADDITIONAL_DC_PARAMS['qdrant_ui_port'],

    'QDRANT_LOCAL_VOLUME': DENSE_DB_PATH
}

# open search
SPARSE_DB_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['KG_DIR_STRUCT']['embeddings_dir']['name']}/{KGENV_PARAMS['KG_DIR_STRUCT']['embeddings_dir']['sparse_part']}"
SPARSE_CONNECTOR_PARAMS = KGCONN_PARAMS['KG_MODEL_CONNECTORS']['embeddings_struc_connection']['nodesdb_config']['sparse_connector']

opensearch_cnt_variables = {
    'OPENSEARCH_CNTNAME': ADDITIONAL_DC_PARAMS['opensearch_cntname'],
    'OPENSEARCH_HOST': ADDITIONAL_DC_PARAMS['opensearch_host'],

    'OPENSEARCH_PORT': SPARSE_CONNECTOR_PARAMS['conn']['port'],
    'OPENSEARCH_PORT2': ADDITIONAL_DC_PARAMS['opensearch_port2'],

    'OPENSEARCH_LOCAL_VOLUME': SPARSE_DB_PATH,
}

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

    'EXTERNAL_SPEC_KG_PATH': SPEC_KG_PATH,
    'EXTERNAL_SPEC_QADS_PATH': f"{EXT_PA_PATH}/{KGENV_PARAMS['PERSONALAI_REPO_DIRS']['qa_datasets']}/{KGHYPERP_PARAMS['DATASET_NAME']}",
    'EXTERNAL_NOTEBOOKS_PATH': f"{EXT_PA_PATH}/{KGENV_PARAMS['PERSONALAI_REPO_DIRS']['notebooks']}",
    'EXTERNAL_SRC_PATH': f"{EXT_PA_PATH}/{KGENV_PARAMS['PERSONALAI_REPO_DIRS']['src']}",
    'EXTERNAL_MODELS_PATH': f"{KGENV_PARAMS['BASE_KG_PATH']}/../{KGENV_PARAMS['PERSONALAI_REPO_DIRS']['models']}",

    'INTERNAL_SPEC_KG_PATH': f"{INT_PA_PATH}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['kg']}/{KGHYPERP_PARAMS['DATASET_NAME']}/{KGHYPERP_PARAMS['KNOWLEDGE_GRAPH_NAME']}",
    'INTERNAL_SPEC_QADS_PATH': f"{INT_PA_PATH}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['qa_datasets']}/{KGHYPERP_PARAMS['DATASET_NAME']}",
    'INTERNAL_NOTEBOOKS_PATH': f"{INT_PA_PATH}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['notebooks']}",
    'INTERNAL_SRC_PATH': f"{INT_PA_PATH}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['src']}",
    'INTERNAL_MODELS_PATH': f"{INT_PA_PATH}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['models']}"
}

compose_variables = {
    'COMPOSE_PROJECT_NAME': f"personalai_mmenshikov_{KGHYPERP_PARAMS['DATASET_NAME']}_{KGHYPERP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"
}

####################################################
print("4. Formating dotenv-file")

def dictvar_to_string(dict_variables) -> str:
    return '\n'.join(list(map(lambda item: f'{item[0]}="{item[1]}"', dict_variables.items())))


def add_prefixes(dict_variables) -> None:
    for k in dict_variables.keys():
        if k.endswith("_CNTNAME"):
            dict_variables[k] = f"{dict_variables[k]}_{KGHYPERP_PARAMS['DATASET_NAME']}_{KGHYPERP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"


env_variables = [
    neo4j_cnt_variables, qdrant_cnt_variables, mongo_cnt_variables, mongoui_cnt_variables,
    redis_cnt_variables, redisui_cnt_variables, opensearch_cnt_variables, workspace_cnt_variables]
for variables in env_variables:
    add_prefixes(variables)
env_variables += [llmagents_cnt_variables, compose_variables]

env_variables = '\n'.join(
    list(map(lambda vars: dictvar_to_string(vars), env_variables)))

####################################################
print("5. Saving dotenv-file")

DC_ENV_PATH = f"{CONTAINER_KG_PATH}/{KGENV_PARAMS['SAVE_CONFIGS_NAMES']['docker_compose_env']}"
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
