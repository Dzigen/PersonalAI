from dataclasses import dataclass, field
from typing import Dict

from .utils import KVDBConnectionConfig
from .configs import DEFAULT_KVDB_CONFIGS, AVAILABLE_KVDB_CONNECTORS

@dataclass
class KeyValueStoreConfig:
    db_vendor: str = 'aerospike'
    db_config: KVDBConnectionConfig = DEFAULT_KVDB_CONFIGS['aerospike']

class KeyValueStore:
    def __init__(self, config: KeyValueStoreConfig = KeyValueStoreConfig()) -> None:
        self.config = config
        self.db_connector = AVAILABLE_KVDB_CONNECTORS[config.db_vendor](config.db_config)

    def get_value_by_key(self, key: object):
        return self.db_connector.read([key])[0]