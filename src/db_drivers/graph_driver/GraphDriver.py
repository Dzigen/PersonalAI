from dataclasses import dataclass, field
from typing import Dict

from .utils import GraphDBConnectionConfig, AbstractGraphDatabaseConnection
from .configs import DEFAULT_GRAPHDB_CONFIGS, AVAILABLE_GRAPHDB_CONNECTORS
from ...utils import Logger

@dataclass
class GraphDriverConfig:
    db_vendor: str = 'neo4j'
    db_config: GraphDBConnectionConfig = field(default_factory=lambda:DEFAULT_GRAPHDB_CONFIGS['neo4j'])

class GraphDriver:
    @staticmethod
    def connect(config: GraphDriverConfig = GraphDriverConfig()) -> AbstractGraphDatabaseConnection:
        return AVAILABLE_GRAPHDB_CONNECTORS[config.db_vendor](config.db_config)
