from dataclasses import field

from .AerospikeConnector import AerospikeConnector, DEFAULT_AEROSPIKE_CONFIG
from .InMemoryConnector import InMemoryConnector, DEFAULT_INMEMORY_CONFIG

DEFAULT_KVDB_CONFIGS = {
    'aerospike': DEFAULT_AEROSPIKE_CONFIG,
    'inmemory': DEFAULT_INMEMORY_CONFIG
}

AVAILABLE_KVDB_CONNECTORS = {
    'aerospike': AerospikeConnector,
    'inmemory': InMemoryConnector
}

# TODO
AVAILABLE_CACHE_CONFIGS = {
    'astar': None
}