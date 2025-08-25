from ...db_drivers.graph_driver import GraphDriverConfig, DEFAULT_NEO4J_CONFIG

GRAPH_DB_DEFAULT_DRIVER_CONFIG = GraphDriverConfig(db_vendor='neo4j', db_config=DEFAULT_NEO4J_CONFIG)
GRAPH_MODEL_LOG_PATH = 'log/kg_model/graph'
