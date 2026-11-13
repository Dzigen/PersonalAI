import pytest
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from typing import Dict

from src.db_drivers.table_driver import TableDriver
from src.db_drivers.tree_driver.utils import AbstractTreeDatabaseConnection

from .available_table_configs import inmemory_table_config, mongo_table_config, \
    sqlite3_table_config, mysql_table_config, postgresql_table_config, available_table_configs

@pytest.fixture(scope='package')
def available_table_connections(available_table_configs):
    connections: Dict[str, AbstractTreeDatabaseConnection] = dict()
    for vendor_name, vendor_config in available_table_configs.items():
        connections[vendor_name] = TableDriver.select(vendor_config)
        connections[vendor_name].open_connection()
    return connections


@pytest.fixture(scope='function')
def tabledb_conn(available_table_connections, request):
    return available_table_connections[request.param]
