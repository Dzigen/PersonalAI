import pytest

import sys
sys.path.insert(0, "../../")
from src.db_drivers.kv_driver import KeyValueDriver, KeyValueDriverConfig, KVDBConnectionConfig

@pytest.fixture()
def inmemory_conn():
    config = KeyValueDriverConfig(db_vendor='inmemory_kv', db_config=KVDBConnectionConfig(
        host='localhost', params={'kvstore_dump_name': 'inmemory_store', 'load_from_disk': False,
        'load_dump_dir': './volumes', 'save_on_disk': True, 'save_dump_dir': './volumes'}, need_to_clear=True))
    return KeyValueDriver.connect(config)

@pytest.fixture()
def aerospike_conn():
    config = KeyValueDriverConfig(db_vendor='aerospike', db_config=KVDBConnectionConfig(
        host='aerospikelservice', port=3000, db_info={'dbname': 'testing', 'table': 'testing'},
        need_to_clear=True))
    return KeyValueDriver.connect(config)
