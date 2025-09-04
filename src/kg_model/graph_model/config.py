from ...db_drivers.graph_driver import GraphDriverConfig
from ...db_drivers.graph_driver.configs import DEFAULT_KUZU_CONFIG

GRAPH_DB_DEFAULT_DRIVER_CONFIG = GraphDriverConfig(db_vendor='kuzu', db_config=DEFAULT_KUZU_CONFIG)
GRAPH_MODEL_LOG_PATH = 'log/kg_model/graph'
