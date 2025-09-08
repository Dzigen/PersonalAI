from ..utils import KVDBConnectionConfig

DEFAULT_AEROSPIKE_CONFIG = KVDBConnectionConfig(
    host='localhost', port=3000)

DEFAULT_INMEMORYKV_CONFIG = KVDBConnectionConfig(
    host='localhost',
    params={
        'kvstore_dump_name': 'inmemory_store',
        'load_from_disk': False, 'load_dump_dir': '.',
        'save_on_disk': True, 'save_dump_dir': '.',
        'max_storage': 5e+8
    })

DEFAULT_MONGOKV_CONFIG = KVDBConnectionConfig(
    host='localhost', port=27017,
    db_info={'db': 'test_db', 'table': 'test_collection'},
    params={'username': 'user', 'password': 'pass', 'max_storage': -1})

DEFAULT_REDISKV_CONFIG = KVDBConnectionConfig(
    host='localhost', port=6380, need_to_clear=False,
    db_info={'db': 0, 'table': 'test_collection'},
    params={'ss_name': 'sorted_node_pairs', 'hs_name': 'node_pairs', 'max_storage': 5e+8})

DEFAULT_MIXEDKV_CONFIG = KVDBConnectionConfig(
    params={'redis_config': DEFAULT_REDISKV_CONFIG, 'mongo_config': DEFAULT_MONGOKV_CONFIG})
