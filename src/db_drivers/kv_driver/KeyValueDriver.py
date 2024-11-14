from dataclasses import dataclass, field
from typing import Dict

from .utils import KVDBConnectionConfig, AbstractKVDatabaseConnection
from .configs import DEFAULT_KVDB_CONFIGS, AVAILABLE_KVDB_CONNECTORS

@dataclass
class KeyValueDriverConfig:
    #: TODO
    db_vendor: str = 'aerospike'
    #: TODO
    db_config: KVDBConnectionConfig = field(default_factory=lambda: DEFAULT_KVDB_CONFIGS['aerospike'])

class KeyValueDriver:
    """_summary_"""

    @staticmethod
    def connect(config: KeyValueDriverConfig = KeyValueDriverConfig()) -> AbstractKVDatabaseConnection:
        return AVAILABLE_KVDB_CONNECTORS[config.db_vendor](config.db_config)
