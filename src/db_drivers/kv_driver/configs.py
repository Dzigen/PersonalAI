from .connectors.AerospikeConnector import AerospikeConnector, DEFAULT_AEROSPIKE_CONFIG
from .connectors.InMemoryKVConnector import InMemoryKVConnector, DEFAULT_INMEMORYKV_CONFIG

DEFAULT_KVDB_CONFIGS = {
    'aerospike': DEFAULT_AEROSPIKE_CONFIG,
    'inmemory_kv': DEFAULT_INMEMORYKV_CONFIG
}

AVAILABLE_KVDB_CONNECTORS = {
    'aerospike': AerospikeConnector,
    'inmemory_kv': InMemoryKVConnector
}