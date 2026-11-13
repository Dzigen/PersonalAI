import pytest
import sys

from typing import Dict

# TO CHANGE
PROJECT_BASE_DIR = '../'
sys.path.insert(0, PROJECT_BASE_DIR)
TEST_VOLUME_DIR = './volumes'

from src.db_drivers.tree_driver.utils import TreeNodeType
from src.db_drivers.tree_driver import TreeDriver, TreeDriverConfig, TreeDBConnectionConfig
from src.db_drivers.tree_driver.utils import AbstractTreeDatabaseConnection


from .available_tree_configs import kuzu_tree_config, \
    neo4j_tree_config, available_tree_configs

@pytest.fixture(scope='package')
def available_tree_connections(available_tree_configs) -> Dict[str, AbstractTreeDatabaseConnection]:
    connections: Dict[str, AbstractTreeDatabaseConnection] = dict()
    for vendor_name, vendor_config in available_tree_configs.items():
        connections[vendor_name] = TreeDriver.select(vendor_config)
        connections[vendor_name].open_connection()
    return connections


@pytest.fixture(scope='function')
def treedb_conn(available_tree_connections, request):
    return available_tree_connections[request.param]
