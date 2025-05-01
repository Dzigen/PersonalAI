from .connectors.Neo4jConnector import Neo4jConnector, DEFAULT_NEO4J_CONFIG

DEFAULT_TREEDB_CONFIGS = {
    'neo4j': DEFAULT_NEO4J_CONFIG
}

AVAILABLE_TREEDB_CONNECTORS = {
    'neo4j': Neo4jConnector
}
