from ..db_drivers.kv_driver import KeyValueDriverConfig, KVDBConnectionConfig


DP_MAIN_LOG_PATH = 'log/dialogue_processing/main'

DEFAULT_DIAG_PROC_KVCACHE_CONFIG = KeyValueDriverConfig(
    db_vendor='inmemory_kv',
    db_config=KVDBConnectionConfig(
        host='localhost',
        params={
            'load_from_disk': True,
            'load_dump_name': None,
            'load_dump_dir': './diag_proc_tmp/cache/inmemory_kv',
            'save_on_disk': True, 'save_dump_dir': './diag_proc_tmp/cache/inmemory_kv',
            'max_storage': 5e+8
        },
        need_to_clear=False
    ),
)
