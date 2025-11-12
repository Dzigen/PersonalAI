from typing import Dict
from .connectors import Neo4jGraphConnector, InMemoryGraphConnector, KuzuGraphConnector
from .connectors.configs import DEFAULT_INMEMORYGRAPH_CONFIG, DEFAULT_KUZU_CONFIG, DEFAULT_NEO4J_CONFIG
from .utils import AbstractGraphDatabaseConnection, GraphDBConnectionConfig

DEFAULT_GRAPHDB_CONFIGS: Dict[str, GraphDBConnectionConfig] = {
    'neo4j': DEFAULT_NEO4J_CONFIG,
    'inmemory_graph': DEFAULT_INMEMORYGRAPH_CONFIG,
    'kuzu': DEFAULT_KUZU_CONFIG
}

AVAILABLE_GRAPHDB_CONNECTORS: Dict[str, AbstractGraphDatabaseConnection] = {
    'neo4j': Neo4jGraphConnector,
    'inmemory_graph': InMemoryGraphConnector,
    'kuzu': KuzuGraphConnector
}
