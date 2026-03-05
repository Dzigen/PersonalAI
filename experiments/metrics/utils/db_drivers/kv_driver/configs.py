from typing import Dict

from .connectors import InMemoryKVConnector, MixedKVConnector, RedisKVConnector, MongoKVConnector
from .connectors.configs import DEFAULT_INMEMORYKV_CONFIG, DEFAULT_REDISKV_CONFIG, \
    DEFAULT_MONGOKV_CONFIG, DEFAULT_MIXEDKV_CONFIG
from .utils import AbstractKVDatabaseConnection, KVDBConnectionConfig

DEFAULT_KVDB_CONFIGS: Dict[str, KVDBConnectionConfig] = {
    'inmemory_kv': DEFAULT_INMEMORYKV_CONFIG,
    'redis': DEFAULT_REDISKV_CONFIG,
    'mongo': DEFAULT_MONGOKV_CONFIG,
    'mixed_kv': DEFAULT_MIXEDKV_CONFIG
}

AVAILABLE_KVDB_CONNECTORS: Dict[str, AbstractKVDatabaseConnection] = {
    'inmemory_kv': InMemoryKVConnector,
    'redis': RedisKVConnector,
    'mongo': MongoKVConnector,
    'mixed_kv': MixedKVConnector
}
