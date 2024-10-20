from dataclasses import dataclass, field
from typing import Dict

from .utils import KVDBConnectionConfig, AbstractKVDatabaseConnection
from .configs import DEFAULT_KVDB_CONFIGS, AVAILABLE_KVDB_CONNECTORS

@dataclass
class KeyValueDriverConfig:
    """_summary_
    """
    #
    db_vendor: str = 'aerospike'
    #
    db_config: KVDBConnectionConfig = field(default_factory=lambda:DEFAULT_KVDB_CONFIGS['aerospike'])

class KeyValueDriver:
    @staticmethod
    def connect(config: KeyValueDriverConfig = KeyValueDriverConfig()) -> AbstractKVDatabaseConnection:
        """_summary_

        :param config: _description_, defaults to KeyValueDriverConfig()
        :type config: KeyValueDriverConfig, optional
        :return: _description_
        :rtype: AbstractKVDatabaseConnection
        """
        return AVAILABLE_KVDB_CONNECTORS[config.db_vendor](config.db_config)