import pytest
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from typing import Dict

from src.db_drivers.kv_driver import KeyValueDriver, KeyValueDriverConfig, KVDBConnectionConfig
from src.db_drivers.kv_driver.utils import AbstractKVDatabaseConnection
from .available_kv_configs import inmemory_kv_config, redis_kv_config, mongo_kv_config, \
    mixed_kv_config, available_kv_configs

@pytest.fixture(scope='package')
def available_kv_connections(available_kv_configs):
    connections: Dict[str, AbstractKVDatabaseConnection] = dict()
    for vendor_name, vendor_config in available_kv_configs.items():
        connections[vendor_name] = KeyValueDriver.select(vendor_config)
        connections[vendor_name].open_connection()
    return connections


@pytest.fixture(scope='function')
def kvdb_conn(available_kv_connections, request):
    return available_kv_connections[request.param]
