from .connectors import InMemoryKVConnector, MixedKVConnector, \
    RedisKVConnector, MongoKVConnector
from .connectors.configs import DEFAULT_INMEMORYKV_CONFIG, DEFAULT_REDISKV_CONFIG, \
    DEFAULT_MONGOKV_CONFIG, DEFAULT_MIXEDKV_CONFIG

DEFAULT_KVDB_CONFIGS = {
    # 'aerospike': DEFAULT_AEROSPIKE_CONFIG,
    'inmemory_kv': DEFAULT_INMEMORYKV_CONFIG,
    'redis': DEFAULT_REDISKV_CONFIG,
    'mongo': DEFAULT_MONGOKV_CONFIG,
    'mixed_kv': DEFAULT_MIXEDKV_CONFIG
}

AVAILABLE_KVDB_CONNECTORS = {
    # 'aerospike': AerospikeKVConnector,
    'inmemory_kv': InMemoryKVConnector,
    'redis': RedisKVConnector,
    'mongo': MongoKVConnector,
    'mixed_kv': MixedKVConnector
}
