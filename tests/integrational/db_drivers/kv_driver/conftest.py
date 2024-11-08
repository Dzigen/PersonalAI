import pytest

import sys
sys.path.insert(0, "../../")
from src.db_drivers.kv_driver import KeyValueDriver, KeyValueDriverConfig, KVDBConnectionConfig

@pytest.fixture()
def inmemory_conn():
    config = KeyValueDriverConfig(db_vendor='inmemory', db_config=KVDBConnectionConfig(
        need_to_clear=True))
    return KeyValueDriver.connect(config)

@pytest.fixture()
def aerospike_conn():
    config = KeyValueDriverConfig(db_vendor='aerospike', db_config=KVDBConnectionConfig(
        db_info={'dbname': 'testing', 'table': 'testing'},
        need_to_clear=True))
    return KeyValueDriver.connect(config)
