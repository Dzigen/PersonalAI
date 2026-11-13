import pytest
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from copy import deepcopy

from src.db_drivers.table_driver import TableDriverConfig

from src.db_drivers.table_driver.configs import DEFAULT_INMEMORYTABLE_CONFIG, DEFAULT_MONGOTABLE_CONFIG, \
    DEFAULT_MYSQLTABLE_CONFIG, DEFAULT_POSTGRESQLTABLE_CONFIG, DEFAULT_SQLITE3TABLE_CONFIG
from src.utils.agent_stat_analyzer.utils import LLMInferenceStat

CREATE_TABLE_QUERY = '''
    CREATE TABLE IF NOT EXISTS testing (
        id SERIAL PRIMARY KEY,
        prompt_tokens_amount INT NULL,
        generated_tokens_amount INT NULL,
        preparation_elapsed_time REAL NULL,
        inference_elapsed_time REAL NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
    '''

@pytest.fixture(scope='session')
def inmemory_table_config():
    config = TableDriverConfig(
        db_vendor='inmemory_table', 
        db_config=deepcopy(DEFAULT_INMEMORYTABLE_CONFIG)
    )
    config.db_config.need_to_clear = True # !!! PAY ATTENTION !!!
    config.db_config.db_info['db'] = 'testing'
    config.db_config.db_info['table'] = 'testing'
    config.db_config.db_info['table_info'] = LLMInferenceStat
    config.db_config.db_info['expected_db_base_path'] = TEST_VOLUME_DIR
    return config

@pytest.fixture(scope='session')
def mongo_table_config():
    config = TableDriverConfig(
        db_vendor='mongo', 
        db_config=deepcopy(DEFAULT_MONGOTABLE_CONFIG)
    )
    config.db_config.need_to_clear = True # !!! PAY ATTENTION !!!
    config.db_config.db_info['db'] = 'testing'
    config.db_config.db_info['table'] = 'testing'
    config.db_config.db_info['table_info'] = LLMInferenceStat
    config.db_config.db_info['expected_db_base_path'] = TEST_VOLUME_DIR
    return config

@pytest.fixture(scope='session')
def sqlite3_table_config():
    config = TableDriverConfig(
        db_vendor='sqlite3', 
        db_config=deepcopy(DEFAULT_SQLITE3TABLE_CONFIG)
    )
    config.db_config.need_to_clear = True # !!! PAY ATTENTION !!!
    config.db_config.db_info['db'] = 'testing'
    config.db_config.db_info['table'] = 'testing'
    config.db_config.db_info['table_info'] = LLMInferenceStat
    config.db_config.db_info['create_table_query'] = CREATE_TABLE_QUERY
    config.db_config.db_info['expected_db_base_path'] = TEST_VOLUME_DIR
    return config

@pytest.fixture(scope='session')
def mysql_table_config():
    config = TableDriverConfig(
        db_vendor='mysql', 
        db_config=deepcopy(DEFAULT_MYSQLTABLE_CONFIG)
    )
    config.db_config.need_to_clear = True # !!! PAY ATTENTION !!!
    config.db_config.db_info['db'] = 'testing'
    config.db_config.db_info['table'] = 'testing'
    config.db_config.db_info['table_info'] = LLMInferenceStat
    config.db_config.db_info['create_table_query'] = CREATE_TABLE_QUERY
    config.db_config.db_info['expected_db_base_path'] = TEST_VOLUME_DIR
    return config

@pytest.fixture(scope='session')
def postgresql_table_config():
    config = TableDriverConfig(
        db_vendor='postgresql', 
        db_config=deepcopy(DEFAULT_POSTGRESQLTABLE_CONFIG)
    )
    config.db_config.need_to_clear = True # !!! PAY ATTENTION !!!
    config.db_config.db_info['db'] = 'testing'
    config.db_config.db_info['table'] = 'testing'
    config.db_config.db_info['table_info'] = LLMInferenceStat
    config.db_config.db_info['create_table_query'] = CREATE_TABLE_QUERY
    config.db_config.db_info['expected_db_base_path'] = TEST_VOLUME_DIR
    return config

@pytest.fixture(scope='session')
def available_table_configs(
    inmemory_table_config, mongo_table_config, 
    sqlite3_table_config, mysql_table_config, postgresql_table_config
    ):
    return {
        'inmemory_table': inmemory_table_config,
        'mongo': mongo_table_config,
        'sqlite3': sqlite3_table_config,
        'mysql': mysql_table_config,
        'postgresql': postgresql_table_config
    }