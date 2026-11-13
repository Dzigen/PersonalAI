from .db_drivers.kv_driver import KeyValueDriverConfig, KVDBConnectionConfig
from .utils.agent_stat_analyzer import AgentStatAnalyzerConfig

PAI_MAIN_LOG_PATH = "log/main"

TEXTIDSTORE_LOG_PATH = "log/textid_store"

DEFAULT_PERSONALAI_KVCACHE_CONFIG = KeyValueDriverConfig(
    db_vendor='inmemory_kv',
    db_config=KVDBConnectionConfig(
        host='localhost',
        params={
            'load_from_disk': True,
            'save_on_disk': True,
            'max_storage': 5e+8,
            'rewrite': True
        },
        need_to_clear=False
    ),
)

DEFAULT_TEXTTOTRIPLETS_STORE_CONFIG = KeyValueDriverConfig(
    db_vendor='inmemory_kv',
    db_config=KVDBConnectionConfig(
        host='localhost',
        db_info={'db': 'DefaultPersonalAIKVDB', 'table': 'textidtotripletsidmaptable'},
        params={
            'load_from_disk': True,
            'save_on_disk': True,
            'max_storage': 5e+8,
            'rewrite': True
        },
        need_to_clear=False
    ),
)

DEFAULT_TRIPLETTOTEXTS_STORE_CONFIG = KeyValueDriverConfig(
    db_vendor='inmemory_kv',
    db_config=KVDBConnectionConfig(
        host='localhost',
        db_info={'db': 'DefaultPersonalAIKVDB', 'table': 'tripletidtotextsidmaptable'},
        params={
            'load_from_disk': True,
            'save_on_disk': True,
            'max_storage': 5e+8,
            'rewrite': True
        },
        need_to_clear=False
    ),
)

DEFAULT_AGENTSTAT_CONFIG = AgentStatAnalyzerConfig()