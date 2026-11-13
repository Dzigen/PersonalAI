from ...db_drivers.kv_driver import KeyValueDriverConfig, KVDBConnectionConfig


DEFAULT_CACHEKV_CONFIG = KeyValueDriverConfig(
    db_vendor='inmemory_kv',
    db_config=KVDBConnectionConfig(
        host='localhost',
        params={
            'save_on_disk': True,
            'max_storage': 5e+8,
            'rewrite': True
        },
        need_to_clear=False
    ),
)
