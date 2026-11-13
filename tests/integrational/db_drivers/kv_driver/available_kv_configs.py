import pytest
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from copy import deepcopy
from src.db_drivers.kv_driver import KeyValueDriverConfig
from src.db_drivers.kv_driver.configs import DEFAULT_INMEMORYKV_CONFIG, DEFAULT_MIXEDKV_CONFIG, \
    DEFAULT_MONGOKV_CONFIG, DEFAULT_REDISKV_CONFIG

@pytest.fixture(scope='session')
def inmemory_kv_config():
    config = KeyValueDriverConfig(
        db_vendor='inmemory_kv', 
        db_config=deepcopy(DEFAULT_INMEMORYKV_CONFIG)
    )
    config.db_config.need_to_clear = True # !!! PAY ATTENTION !!!
    config.db_config.db_info['db'] = 'testing'
    config.db_config.db_info['table'] = 'testing'
    config.db_config.db_info['expected_db_base_path'] = TEST_VOLUME_DIR
    return config

@pytest.fixture(scope='session')
def redis_kv_config():
    config = KeyValueDriverConfig(
        db_vendor='redis', 
        db_config=deepcopy(DEFAULT_REDISKV_CONFIG)
    )
    config.db_config.need_to_clear = True # !!! PAY ATTENTION !!!
    config.db_config.db_info['db'] = 0 # !!! PAY ATTENTION !!!
    config.db_config.db_info['table'] = 'testing'
    config.db_config.db_info['expected_db_base_path'] = TEST_VOLUME_DIR
    return config

@pytest.fixture(scope='session')
def mongo_kv_config():
    config = KeyValueDriverConfig(
        db_vendor='mongo', 
        db_config=deepcopy(DEFAULT_MONGOKV_CONFIG)
    )
    config.db_config.need_to_clear = True # !!! PAY ATTENTION !!!
    config.db_config.db_info['db'] = 'testing'
    config.db_config.db_info['table'] = 'testing'
    config.db_config.db_info['expected_db_base_path'] = TEST_VOLUME_DIR
    return config


@pytest.fixture(scope='session')
def mixed_kv_config(redis_kv_config, mongo_kv_config):
    config = KeyValueDriverConfig(
        db_vendor='mixed_kv', 
        db_config=deepcopy(DEFAULT_MIXEDKV_CONFIG)
    )
    config.db_config.need_to_clear = True # !!! PAY ATTENTION !!!
    config.db_config.db_info['db'] = 'testing'
    config.db_config.db_info['table'] = 'testing'
    config.db_config.db_info['expected_db_base_path'] = TEST_VOLUME_DIR
    config.db_config.params['redis_config'] = deepcopy(redis_kv_config.db_config)
    config.db_config.params['mongo_config'] = deepcopy(mongo_kv_config.db_config)
    return config

@pytest.fixture(scope='session')
def available_kv_configs(
    inmemory_kv_config, redis_kv_config,
    mongo_kv_config, mixed_kv_config
):
    return {
        'inmemory_kv': inmemory_kv_config,
        'redis': redis_kv_config,
        'mongo': mongo_kv_config,
        'mixed_kv': mixed_kv_config
    }