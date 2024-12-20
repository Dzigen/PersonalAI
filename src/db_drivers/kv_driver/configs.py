from .connectors  import \
    AerospikeConnector, DEFAULT_AEROSPIKE_CONFIG,\
    InMemoryKVConnector, DEFAULT_INMEMORYKV_CONFIG,\
    MixedKVConnector, DEFAULT_MIXEDKV_CONFIG,\
    RedisConnector, DEFAULT_REDISKV_CONFIG,\
    MongoConnector, DEFAULT_MONGOKV_CONFIG

DEFAULT_KVDB_CONFIGS = {
    'aerospike': DEFAULT_AEROSPIKE_CONFIG,
    'inmemory_kv': DEFAULT_INMEMORYKV_CONFIG,
    'redis': DEFAULT_REDISKV_CONFIG,
    'mongo': DEFAULT_MONGOKV_CONFIG,
    'mixed_kv': DEFAULT_MIXEDKV_CONFIG
}

AVAILABLE_KVDB_CONNECTORS = {
    'aerospike': AerospikeConnector,
    'inmemory_kv': InMemoryKVConnector,
    'redis': RedisConnector,
    'mongo': MongoConnector,
    'mixed_kv': MixedKVConnector
}
