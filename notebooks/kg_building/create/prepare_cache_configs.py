print("Creating MemPipeline config file...")
import sys
import joblib
import yaml

####################################################
print("1. Loading hyperparameters from .yaml files")

# Read YAML file (kg-conn)
KGCONN_FILE_PATH = sys.orig_argv[2]
with open(KGCONN_FILE_PATH, 'r') as stream:
    KGCONN_PARAMS = yaml.safe_load(stream)

# Read YAML file (kg-env)
KGENV_FILE_PATH = sys.orig_argv[3]
with open(KGENV_FILE_PATH, 'r') as stream:
    KGENV_PARAMS = yaml.safe_load(stream)

# Read YAML file (kg-hyperp)
KGHYPERP_FILE_PATH = sys.orig_argv[4]
with open(KGHYPERP_FILE_PATH, 'r') as stream:
    KGHYPERP_PARAMS = yaml.safe_load(stream)

sys.path.insert(0, KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path'])

from src.db_drivers.kv_driver import KeyValueDriverConfig, KVDBConnectionConfig
from src.utils.agent_stat_analyzer import AgentStatAnalyzerConfig
from src.db_drivers.table_driver import TableDBConnectionConfig, TableDriverConfig

####################################################
print("2. Setting paths")

DATASET_KGS_PATH = f"{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['kg']}{KGENV_PARAMS['DATASET_NAME']}"
SPEC_KG_PATH = f"{DATASET_KGS_PATH}/{KGENV_PARAMS['KNOWLEDGE_GRAPH_NAME']}"

CACHE_CONFIG_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['SAVE_CONFIGS_NAMES']['kvdriver_cache_config']}"
INFSTAT_CONFIG_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['SAVE_CONFIGS_NAMES']['inference_stat_config']}"

####################################################
print("3. Setting KVCache Config")

KVCACHE_CONFIG = KGCONN_PARAMS['MEM_PIPELINE_CONNECTORS']['kv_cache_connections']
PERSIS_KVC_CONFIG = KVCACHE_CONFIG['persistent_cache_config']
persis_kvc_config = KVDBConnectionConfig(
    db_info=PERSIS_KVC_CONFIG['db_info'],
    params=PERSIS_KVC_CONFIG['params'],
    host=PERSIS_KVC_CONFIG['host'],
    port=PERSIS_KVC_CONFIG['port']
)

RAM_KVC_CONFIG = KVCACHE_CONFIG['ram_cache_config']
ram_kvc_config = KVDBConnectionConfig(
    db_info=RAM_KVC_CONFIG['db_info'],
    params=RAM_KVC_CONFIG['params'],
    host=RAM_KVC_CONFIG['host'],
    port=RAM_KVC_CONFIG['port']
)

kvdriver_config = KeyValueDriverConfig(
    db_vendor='mixed_kv',
    db_config=KVDBConnectionConfig(
        db_info=PERSIS_KVC_CONFIG['db_info'],
        params={
            'redis_config': ram_kvc_config,
            'mongo_config': persis_kvc_config
        }
    )
)

####################################################
print("4. Setting LLMStat Config")

LLMSTAT_TABLE_CONFIG = KGCONN_PARAMS['MEM_PIPELINE_CONNECTORS']['inference_stat_connection']
llmstat_table_config = TableDBConnectionConfig(
    db_info=LLMSTAT_TABLE_CONFIG['db_info'],
    params=LLMSTAT_TABLE_CONFIG['params'],
    host=LLMSTAT_TABLE_CONFIG['host'],
    port=LLMSTAT_TABLE_CONFIG['port']
)

infstat_config = AgentStatAnalyzerConfig(
    table_driver_config=TableDriverConfig(
        db_vendor='mongo',
        db_config=llmstat_table_config
    )
)

####################################################
print("4. Saving KVCahe and LLMStat Configs")

print("kv_driver: ", kvdriver_config)
print("llmstat: ", infstat_config)

joblib.dump(kvdriver_config, CACHE_CONFIG_PATH)
joblib.dump(infstat_config, INFSTAT_CONFIG_PATH)
