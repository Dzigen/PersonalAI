from dataclasses import dataclass, field
from typing import Dict

from .utils import KVDBConnectionConfig, AbstractKVDatabaseConnection
from .configs import DEFAULT_KVDB_CONFIGS, AVAILABLE_KVDB_CONNECTORS

@dataclass
class KeyValueDriverConfig:
    db_vendor: str = 'aerospike'
    db_config: KVDBConnectionConfig = DEFAULT_KVDB_CONFIGS['aerospike']

class KeyValueDriver:
    @staticmethod
    def connect(config: KeyValueDriverConfig = KeyValueDriverConfig()) -> AbstractKVDatabaseConnection:
        return AVAILABLE_KVDB_CONNECTORS[config.db_vendor](config.db_config)