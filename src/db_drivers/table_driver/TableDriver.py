from dataclasses import dataclass, field
from typing import Dict, Union

from .utils import TableDBConnectionConfig, AbstractTableDatabaseConnection
from .configs import DEFAULT_TABLEDB_CONFIGS, AVAILABLE_TABLEDB_CONNECTORS
from ...utils.data_structs import BaseConfigOperations


@dataclass
class TableDriverConfig(BaseConfigOperations):
    db_vendor: str = 'sqlite3'
    db_config: Union[Dict, TableDBConnectionConfig] = field(default_factory=lambda: DEFAULT_TABLEDB_CONFIGS['sqlite3'])

    def to_str(self):
        self.formate_fields()
        return f"{self.db_vendor}|{self.db_config.to_str()}"

    def formate_fields(self):
        if isinstance(self.db_config, dict):
            self.db_config = TableDBConnectionConfig.from_dict(self.db_config)

    @staticmethod
    def from_dict(dict_config: Dict):
        formated_config = TableDriverConfig(**dict_config)
        formated_config.formate_fields()
        return formated_config


class TableDriver:
    @staticmethod
    def connect(config: Union[Dict, TableDriverConfig] = TableDriverConfig()) -> AbstractTableDatabaseConnection:
        if isinstance(config, dict):
            config: TableDriverConfig = TableDriverConfig.from_dict(config)
        else:
            config.formate_fields()

        table_conn: AbstractTableDatabaseConnection = AVAILABLE_TABLEDB_CONNECTORS[config.db_vendor](config.db_config)
        table_conn.open_connection()
        return table_conn
