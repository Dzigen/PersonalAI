import pytest

import sys
# TO CHANGE
PROJECT_BASE_DIR = '../../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.db_drivers.kv_driver import KeyValueDriver, KeyValueDriverConfig, KVDBConnectionConfig

#!!!AVAILABLE KEYVALUE CONNECTIONS!!!#

@pytest.fixture(scope='package')
def inmemory_kv_conn():
    config = KeyValueDriverConfig(db_vendor='inmemory_kv', db_config=KVDBConnectionConfig(
        params={'kvstore_dump_name': 'inmemory_store', 'load_from_disk': False,
        'load_dump_dir': TEST_VOLUME_DIR, 'save_on_disk': True, 'save_dump_dir': TEST_VOLUME_DIR}, need_to_clear=True))
    return KeyValueDriver.connect(config)

@pytest.fixture(scope='package')
def aerospike_conn():
    config = KeyValueDriverConfig(db_vendor='aerospike', db_config=KVDBConnectionConfig(
        host='personalai_test_aerospike', port=3000, db_info={'db': 'test', 'table': 'testing'},
        need_to_clear=True))
    return KeyValueDriver.connect(config)

#------------------------------#

@pytest.fixture(scope='package')
def available_keyvalue_connections(
    aerospike_conn,
    inmemory_kv_conn
):
    return {
        'aerospike': aerospike_conn,
        'inmemory_kv': inmemory_kv_conn
    }

@pytest.fixture(scope='function')
def keyvaluedb_conn(available_keyvalue_connections, request):
    return available_keyvalue_connections[request.param]
