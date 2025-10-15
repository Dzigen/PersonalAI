from .db_drivers.kv_driver import KeyValueDriverConfig, KVDBConnectionConfig

PAI_MAIN_LOG_PATH = "log/main"


DEFAULT_PERSONALAI_KVCACHE_CONFIG = KeyValueDriverConfig(
    db_vendor='inmemory_kv',
    db_config=KVDBConnectionConfig(
        host='localhost',
        params={
            'load_from_disk': True, 'load_dump_dir': './personalai_tmp/cache/inmemory_kv',
            'save_on_disk': True, 'save_dump_dir': './personalai_tmp/cache/inmemory_kv',
            'max_storage': 5e+8
        },
        need_to_clear=False
    ),
)
