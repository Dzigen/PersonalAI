import pytest
import sys
from typing import Dict, List
from copy import deepcopy
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.db_drivers.kv_driver import KeyValueDriverConfig, KVDBConnectionConfig
from src.TextIdStore import TextIdStore, TextIdStoreConfig

#!!!AVAILABLE KEYVALUE CONNECTIONS!!!#

@pytest.fixture(scope='package')
def inmemory_kvdriver_config():
    inmemorykv_config = KVDBConnectionConfig(
        params={
            'load_dump_name': 'inmemory_store',
            'load_from_disk': False,
            'max_storage': 5e+8,
            'load_dump_dir': f"{TEST_VOLUME_DIR}/inmemory_kv",
            'save_on_disk': True,
            'save_dump_dir': f"{TEST_VOLUME_DIR}/inmemory_kv"
        },
        need_to_clear=True)

    driver_config = KeyValueDriverConfig(
        db_vendor='inmemory_kv', db_config=inmemorykv_config)
    return driver_config

@pytest.fixture(scope='package')
def redis_kvdriver_config():
    redis_config = KVDBConnectionConfig(
        host='localhost', port=6370, need_to_clear=True, db_info={'db': 0, 'table': 'test_idsstore_collection'},
        params={'ss_name': 'sorted_node_pairs', 'hs_name': 'node_pairs', 'max_storage': 5e+8})

    driver_config = KeyValueDriverConfig(
        db_vendor='redis', db_config=redis_config)
    return driver_config


@pytest.fixture(scope='package')
def mongo_kvdriver_config():
    mongo_config = KVDBConnectionConfig(
        host='localhost', port=27010, db_info={'db': 'test_db', 'table': 'test_idsstore_collection'},
        params={'username': 'user', 'password': 'pass', 'max_storage': -1}, need_to_clear=True)

    driver_config = KeyValueDriverConfig(
        db_vendor='mongo', db_config=mongo_config)
    return driver_config


@pytest.fixture(scope='package')
def mixed_kvdriver_config():
    redis_config = KVDBConnectionConfig(
        host='localhost', port=6370, need_to_clear=True, db_info={'db': 0, 'table': 'test_idsstore_collection'},
        params={'ss_name': 'sorted_node_pairs', 'hs_name': 'node_pairs', 'max_storage': 5e+8})

    mongo_config = KVDBConnectionConfig(
        host='localhost', port=27010, db_info={'db': 'test_db', 'table': 'test_idsstore_collection'},
        params={'username': 'user', 'password': 'pass', 'max_storage': -1},
        need_to_clear=True)

    mixed_config = KVDBConnectionConfig(
        db_info={'db': 'test_db', 'table': 'test_idsstore_collection'},
        params={'mongo_config': mongo_config, 'redis_config': redis_config})
    driver_config = KeyValueDriverConfig(
        db_vendor='mixed_kv', db_config=mixed_config)

    return driver_config

# ------------------------------#


@pytest.fixture(scope='package')
def available_textidstore_configs(
    inmemory_kvdriver_config,
    redis_kvdriver_config,
    mongo_kvdriver_config,
    mixed_kvdriver_config
):

    kvdrivers: List[List[str, KeyValueDriverConfig]] = [
        ['inmemory_kv', inmemory_kvdriver_config], ['redis', redis_kvdriver_config],
        ['mongo', mongo_kvdriver_config], ['mixed_kv', mixed_kvdriver_config],
    ]
    available_configs: Dict[str, TextIdStoreConfig] = dict()
    for kvdriver_name, kvdriver_config in kvdrivers:
        available_configs[kvdriver_name] = TextIdStoreConfig(
            texttotriplets_store_config=deepcopy(kvdriver_config),
            triplettotexts_store_config=deepcopy(kvdriver_config)
        )
        available_configs[kvdriver_name].texttotriplets_store_config.db_config.db_info['table'] = 'texttotriplets_store'
        available_configs[kvdriver_name].triplettotexts_store_config.db_config.db_info['table'] = 'triplettotexts_store'

    return available_configs


@pytest.fixture(scope='function')
def textidstore_instance(available_textidstore_configs: Dict, request):
    config = available_textidstore_configs[request.param]
    idstore = TextIdStore(config)
    return idstore
