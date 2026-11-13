from ..utils import KVDBConnectionConfig

DEFAULT_AEROSPIKE_CONFIG = KVDBConnectionConfig(
    host='localhost', port=3000)

DEFAULT_INMEMORYKV_CONFIG = KVDBConnectionConfig(
    host='localhost',
    params={
        'save_on_disk': True,
        'max_storage': 5e+8,
        'rewrite': True
    })

DEFAULT_MONGOKV_CONFIG = KVDBConnectionConfig(
    host='localhost', port=27017,
    params={'username': 'user', 'password': 'pass', 'max_storage': -1})

DEFAULT_REDISKV_CONFIG = KVDBConnectionConfig(
    host='localhost', port=6380,
    params={'ss_name': 'sorted_node_pairs', 'hs_name': 'node_pairs', 'max_storage': 5e+8})

DEFAULT_MIXEDKV_CONFIG = KVDBConnectionConfig(
    params={'redis_config': DEFAULT_REDISKV_CONFIG, 'mongo_config': DEFAULT_MONGOKV_CONFIG})
