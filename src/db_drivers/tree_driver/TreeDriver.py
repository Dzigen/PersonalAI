from dataclasses import dataclass, field
from typing import Dict, Union

from .utils import TreeDBConnectionConfig, AbstractTreeDatabaseConnection
from .configs import DEFAULT_TREEDB_CONFIGS, AVAILABLE_TREEDB_CONNECTORS


@dataclass
class TreeDriverConfig:
    db_vendor: str = 'kuzu'
    db_config: Union[Dict, TreeDBConnectionConfig] = field(default_factory=lambda: DEFAULT_TREEDB_CONFIGS['kuzu'])

    def to_str(self):
        self.formate_fields()
        return f"{self.db_vendor}|{self.db_config.to_str()}"

    def formate_fields(self):
        if isinstance(self.db_config, dict):
            self.db_config = TreeDBConnectionConfig.from_dict(self.db_config)

    @staticmethod
    def from_dict(dict_config: Dict):
        formated_config = TreeDriverConfig(**dict_config)
        formated_config.formate_fields()
        return formated_config


class TreeDriver:
    @staticmethod
    def connect(config: Union[Dict, TreeDriverConfig] = TreeDriverConfig()) -> AbstractTreeDatabaseConnection:
        if isinstance(config, dict):
            config: TreeDriverConfig = TreeDriverConfig.from_dict(config)
        else:
            config.formate_fields()

        tree_conn: AbstractTreeDatabaseConnection = AVAILABLE_TREEDB_CONNECTORS[config.db_vendor](config.db_config)
        tree_conn.open_connection()
        return tree_conn
