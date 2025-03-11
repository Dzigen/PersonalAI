import sys
import yaml
import subprocess


# Загружаем конфигурационный файл

# Read YAML file
PARAMS_FILE_PATH = sys.orig_argv[2]
with open(PARAMS_FILE_PATH, 'r') as stream:
    HYPER_PARAMS = yaml.safe_load(stream)

# параметры для графовой бд (neo4j)

DATASET_PATH = f"{HYPER_PARAMS['KGS_BASE_PATH']}/{HYPER_PARAMS['DATASET_NAME']}"
KG_PATH = f"{DATASET_PATH}/{HYPER_PARAMS['KNOWLEDGE_GRAPH_NAME']}"
GRAPH_DB_PATH = f"{KG_PATH}/{HYPER_PARAMS['KG_DIR_STRUCT']['graph_dir_name']}/"

neo4j_cnt_variables = {
    'NEO4j_AUTH_USER': HYPER_PARAMS['KG_DB_CONFIGS']['graphdb_config']['params']['user'],
    'NEO4j_AUTH_PWD': HYPER_PARAMS['KG_DB_CONFIGS']['graphdb_config']['params']['pwd'],
    'NEO4J_LOCAL_VOLUME': GRAPH_DB_PATH,
    'NEO4J_HOST': HYPER_PARAMS['KG_DB_CONFIGS']['graphdb_config']['host'],
    'NEO4J_EXTERNAL_PORT': HYPER_PARAMS['KG_DB_CONFIGS']['graphdb_config']['port'],
}

# параметры для persistent бд (mongo)
KV_DB_PATH = f"{KG_PATH}/{HYPER_PARAMS['KG_DIR_STRUCT']['cache_dir_name']['base']}/"
PERSISTENT_DB_PATH = KV_DB_PATH + f"{HYPER_PARAMS['KG_DIR_STRUCT']['cache_dir_name']['persistant']}/"

mongo_cnt_variables = {
    'MONGO_AUTH_USER': HYPER_PARAMS['MEM_PIPELINE_CONFIG']['persistent_cache_config']['params']['username'],
    'MONGO_AUTH_PWD': HYPER_PARAMS['MEM_PIPELINE_CONFIG']['persistent_cache_config']['params']['password'],
    'MONGO_HOST': HYPER_PARAMS['MEM_PIPELINE_CONFIG']['persistent_cache_config']['host'],
    'MONGO_EXTERNAL_PORT': HYPER_PARAMS['MEM_PIPELINE_CONFIG']['persistent_cache_config']['port'],
    'MONGO_LOCAL_VOLUME': PERSISTENT_DB_PATH,
}

# параметры для ram бд (redis)
RAM_DB_PATH = KV_DB_PATH + f"{HYPER_PARAMS['KG_DIR_STRUCT']['cache_dir_name']['ram']}/"

redis_cnt_variables = {
    'REDIS_HOST': HYPER_PARAMS['MEM_PIPELINE_CONFIG']['ram_cache_config']['host'],
    'REDIS_EXTERNAL_PORT': HYPER_PARAMS['MEM_PIPELINE_CONFIG']['ram_cache_config']['port'],
    'REDIS_LOCAL_VOLUME': RAM_DB_PATH,
    'REDIS_CONFIG': HYPER_PARAMS['MEM_PIPELINE_CONFIG']['ram_cache_config']['db_configuration']
}

# параметры для workspace - окружения
worksapce_cnt_variables = {
    'LOCAL_WORKSPACE_DIR': HYPER_PARAMS['BASE_PERSONALAI_DIR'],
    'LOCAL_VENV_DIR': HYPER_PARAMS['PERSONALAI_VENV_DIR'],
}

# параметры для контейнера с llm-моделями
llmagents_cnt_variables = {
    'LLMAGENTS_HOST': HYPER_PARAMS['MEM_PIPELINE_CONFIG']['agent_config']['credentials']['host'],
    'LLMAGENTS_EXTERNAL_PORT': HYPER_PARAMS['MEM_PIPELINE_CONFIG']['agent_config']['credentials']['port'],
    'LLMAGENT_LOCAL_VOLUME': HYPER_PARAMS['OLLAMA_MODELS_DIR']
}

accepted_volume_dirs = {
    'KG_DIR': f"{HYPER_PARAMS['KGS_BASE_PATH']}/{HYPER_PARAMS['DATASET_NAME']}/{HYPER_PARAMS['KNOWLEDGE_GRAPH_NAME']}",
    'QA_DATASET': HYPER_PARAMS['DATASET_PATH'],
    'NOTEBOOKS': f"{HYPER_PARAMS['BASE_PERSONALAI_DIR']}/notebooks",
    'SRC': f"{HYPER_PARAMS['BASE_PERSONALAI_DIR']}/src",
    'MODELS': f"{HYPER_PARAMS['BASE_PERSONALAI_DIR']}/models",
}

def dictvar_to_string(dict_variables) -> str:
    return '\n'.join(list(map(lambda item: f'{item[0]}="{item[1]}"', dict_variables.items())))


env_variables = [neo4j_cnt_variables, mongo_cnt_variables, redis_cnt_variables,
                 worksapce_cnt_variables, llmagents_cnt_variables, accepted_volume_dirs]
env_variables = '\n'.join(list(map(lambda vars: dictvar_to_string(vars), env_variables)))

DC_ENV_PATH = f"{KG_PATH}/{HYPER_PARAMS['SAVE_CONFIGS_NAMES']['docker_compose_env']}"
with open(DC_ENV_PATH, 'w', encoding='utf-8') as fd:
    fd.write(env_variables)
