from typing import Dict

from .connectors import Neo4jTreeConnector
from .connectors import KuzuTreeConnector
from .connectors.configs import DEFAULT_KUZUTREE_CONFIG, DEFAULT_NEO4JTREE_CONFIG
from .utils import TreeDBConnectionConfig, AbstractTreeDatabaseConnection

DEFAULT_TREEDB_CONFIGS: Dict[str, TreeDBConnectionConfig] = {
    'neo4j': DEFAULT_NEO4JTREE_CONFIG,
    'kuzu': DEFAULT_KUZUTREE_CONFIG
}

AVAILABLE_TREEDB_CONNECTORS: Dict[str, AbstractTreeDatabaseConnection] = {
    'neo4j': Neo4jTreeConnector,
    'kuzu': KuzuTreeConnector
}
