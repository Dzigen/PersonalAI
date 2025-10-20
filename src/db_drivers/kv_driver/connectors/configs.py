from ..utils import KVDBConnectionConfig

DEFAULT_AEROSPIKE_CONFIG = KVDBConnectionConfig(
    host='localhost', port=3000)

DEFAULT_INMEMORYKV_CONFIG = KVDBConnectionConfig(
    host='localhost',
    params={
        'load_from_disk': False,
        'load_dump_name': None,
        'load_dump_dir': "./personalai_tmp/volumes/inmemory_kv",
        'save_on_disk': True, 'save_dump_dir': "./personalai_tmp/volumes/inmemory_kv",
        'max_storage': 5e+8
    })

DEFAULT_MONGOKV_CONFIG = KVDBConnectionConfig(
    host='localhost', port=27017,
    params={'username': 'user', 'password': 'pass', 'max_storage': -1})

DEFAULT_REDISKV_CONFIG = KVDBConnectionConfig(
    host='localhost', port=6380, need_to_clear=False,
    params={'ss_name': 'sorted_node_pairs', 'hs_name': 'node_pairs', 'max_storage': 5e+8})

DEFAULT_MIXEDKV_CONFIG = KVDBConnectionConfig(
    params={'redis_config': DEFAULT_REDISKV_CONFIG, 'mongo_config': DEFAULT_MONGOKV_CONFIG})
