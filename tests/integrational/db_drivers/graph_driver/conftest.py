import sys
import pytest
from typing import Dict
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.db_drivers.graph_driver import GraphDriver, GraphDriverConfig, GraphDBConnectionConfig
from src.utils.data_structs import NodeType, RelationType
from src.db_drivers.graph_driver.utils import AbstractGraphDatabaseConnection
from .available_graph_configs import inmemory_graph_config, neo4j_graph_config, \
    kuzu_graph_config, falkordb_graph_config, blazegraph_graph_config, \
        available_graph_configs

@pytest.fixture(scope='package')
def available_graph_connections(available_graph_configs):
    connections: Dict[str, AbstractGraphDatabaseConnection] = dict()
    for vendor_name, vendor_config in available_graph_configs.items():
        connections[vendor_name] = GraphDriver.select(vendor_config)
        connections[vendor_name].open_connection()
    return connections

@pytest.fixture(scope='function')
def graphdb_conn(available_graph_connections, request):
    return available_graph_connections[request.param]
