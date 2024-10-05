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

    def get_value_by_key(self, key: object) -> Dict:
        return self.db_connector.read([key])[0]
    
    def save_kv_pair(self, key, value) -> None:
        self.db_connector.create([key], [value])
    
    def is_key_exists(self, key: object) -> bool:
        return self.db_connector.key_exist(key)