from dataclasses import dataclass, field
from typing import Dict, Union
from .utils import GraphDBConnectionConfig, AbstractGraphDatabaseConnection
from .configs import DEFAULT_GRAPHDB_CONFIGS, AVAILABLE_GRAPHDB_CONNECTORS
from ...utils.data_structs import BaseConfigOperations


@dataclass
class GraphDriverConfig(BaseConfigOperations):
    db_vendor: str = 'kuzu'
    db_config: Union[Dict, GraphDBConnectionConfig] = field(default_factory=lambda: DEFAULT_GRAPHDB_CONFIGS['kuzu'])

    def to_str(self):
        self.formate_fields()
        return f"{self.db_vendor}|{self.db_config.to_str()}"

    def formate_fields(self):
        if isinstance(self.db_config, dict):
            self.db_config = GraphDBConnectionConfig.from_dict(self.db_config)

    @staticmethod
    def from_dict(dict_config: Dict):
        formated_config = GraphDriverConfig(**dict_config)
        formated_config.formate_fields()
        return formated_config


class GraphDriver:
    @staticmethod
    def connect(config: Union[Dict, GraphDriverConfig] = GraphDriverConfig()) -> AbstractGraphDatabaseConnection:
        if isinstance(config, dict):
            config: GraphDriverConfig = GraphDriverConfig.from_dict(config)
        else:
            config.formate_fields()

        graph_conn: AbstractGraphDatabaseConnection = AVAILABLE_GRAPHDB_CONNECTORS[config.db_vendor](config.db_config)
        graph_conn.open_connection()
        return graph_conn
