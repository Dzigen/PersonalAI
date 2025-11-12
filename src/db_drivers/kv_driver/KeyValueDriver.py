from dataclasses import dataclass, field
from typing import Dict, Union
from copy import deepcopy

from .utils import KVDBConnectionConfig, AbstractKVDatabaseConnection
from .configs import DEFAULT_KVDB_CONFIGS, AVAILABLE_KVDB_CONNECTORS
from ...utils.data_structs import BaseConfigOperations


@dataclass
class KeyValueDriverConfig(BaseConfigOperations):
    db_vendor: str = 'inmemory_kv'
    db_config: Union[Dict, KVDBConnectionConfig] = field(default_factory=lambda: DEFAULT_KVDB_CONFIGS['inmemory_kv'])

    def to_str(self):
        self.formate_fields()
        return f"{self.db_vendor}|{self.db_config.to_str()}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = KeyValueDriverConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.db_config, dict):
            self.db_config = KVDBConnectionConfig.from_dict(self.db_config)


class KeyValueDriver:
    @staticmethod
    def connect(config: Union[Dict, KeyValueDriverConfig] = KeyValueDriverConfig()) -> AbstractKVDatabaseConnection:
        if isinstance(config, dict):
            config: KeyValueDriverConfig = KeyValueDriverConfig.from_dict(config)
        else:
            config.formate_fields()

        kv_conn: AbstractKVDatabaseConnection = AVAILABLE_KVDB_CONNECTORS[config.db_vendor](config.db_config)
        kv_conn.open_connection()
        return kv_conn
