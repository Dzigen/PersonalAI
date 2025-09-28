from .connectors import Neo4jTreeConnector
from .connectors import KuzuTreeConnector
from .connectors.configs import DEFAULT_KUZUTREE_CONFIG, DEFAULT_NEO4JTREE_CONFIG

DEFAULT_TREEDB_CONFIGS = {
    'neo4j': DEFAULT_NEO4JTREE_CONFIG,
    'kuzu': DEFAULT_KUZUTREE_CONFIG
}

AVAILABLE_TREEDB_CONNECTORS = {
    'neo4j': Neo4jTreeConnector,
    'kuzu': KuzuTreeConnector
}
