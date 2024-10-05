from dataclasses import field

from .AerospikeConnector import AerospikeConnector, DEFAULT_AEROSPIKE_CONFIG

DEFAULT_KVDB_CONFIGS = {
    'aerospike': DEFAULT_AEROSPIKE_CONFIG
}

AVAILABLE_KVDB_CONNECTORS = {
    'aerospike': AerospikeConnector
}

# TODO
AVAILABLE_CACHE_CONFIGS = {
    'astar': None
}