import pytest
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.db_drivers.table_driver import TableDriverConfig, TableDBConnectionConfig
from src.utils.agent_stat_analyzer.utils import LLMInferenceStat

from src.utils.agent_stat_analyzer import AgentStatAnalyzerConfig

#!!!AVAILABLE TABLE CONNECTIONS!!!#

CREATE_TABLE_QUERY = '''
    CREATE TABLE IF NOT EXISTS test_table (
        id SERIAL PRIMARY KEY,
        prompt_tokens_amount INT NULL,
        generated_tokens_amount INT NULL,
        preparation_elapsed_time REAL NULL,
        inference_elapsed_time REAL NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
    '''

@pytest.fixture(scope='session')
def inmemory_table_agentstat_config():
    inmemory_config = TableDBConnectionConfig(
        db_info={
            'db': 'testing', 'table': 'testing',
            'table_info': LLMInferenceStat, 
            'expected_db_base_path': TEST_VOLUME_DIR
        },
        params={
            'max_storage': 5e+8,
            'save_on_disk': True,
            'rewrite': True
        },
        need_to_clear=True)

    driver_config = TableDriverConfig(
        db_vendor='inmemory_table', db_config=inmemory_config)
    return AgentStatAnalyzerConfig(table_driver_config=driver_config)

@pytest.fixture(scope='session')
def mongo_table_agentstat_config():
    mongo_config = TableDBConnectionConfig(
        host='localhost', port=27017, db_info={
            'db': 'testing', 'table': 'testing', 'table_info': LLMInferenceStat},
        params={'username': 'user', 'password': 'pass', 'max_storage': -1}, need_to_clear=True)

    driver_config = TableDriverConfig(
        db_vendor='mongo', db_config=mongo_config)
    return AgentStatAnalyzerConfig(table_driver_config=driver_config)

@pytest.fixture(scope='session')
def sqlite3_agentstat_config():

    sqlite3_config = TableDBConnectionConfig(
        db_info={
            'db': 'testing', 'table': 'testing',
            'table_info': LLMInferenceStat,
            'create_table_query': CREATE_TABLE_QUERY,
            'expected_db_base_path': TEST_VOLUME_DIR
        },
        need_to_clear=True)

    driver_config = TableDriverConfig(
        db_vendor='sqlite3', db_config=sqlite3_config)
    return AgentStatAnalyzerConfig(table_driver_config=driver_config)

@pytest.fixture(scope='session')
def mysql_agentstat_config():
    mysql_config = TableDBConnectionConfig(
        host='localhost', port=3306, db_info={
            'db': 'testing', 'table': 'testing',
            'table_info': LLMInferenceStat, 'create_table_query': CREATE_TABLE_QUERY,
            'expected_db_base_path': TEST_VOLUME_DIR},
        params={'username': 'personalai', 'password': 'personalai'},
        need_to_clear=True)

    driver_config = TableDriverConfig(
        db_vendor='mysql', db_config=mysql_config)
    return AgentStatAnalyzerConfig(table_driver_config=driver_config)

@pytest.fixture(scope='session')
def postgresql_agentstat_config():

    postgresql_config = TableDBConnectionConfig(
        host='localhost', port=5432, db_info={
            'db': 'testing', 'table': 'testing',
            'table_info': LLMInferenceStat,
            'create_table_query': CREATE_TABLE_QUERY,
            'expected_db_base_path': TEST_VOLUME_DIR},
        params={'username': 'personalai', 'password': 'personalai'},
        need_to_clear=True)

    driver_config = TableDriverConfig(
        db_vendor='postgresql', db_config=postgresql_config)
    return AgentStatAnalyzerConfig(table_driver_config=driver_config)

@pytest.fixture(scope='session')
def available_agentstatanalyzer_configs(
    inmemory_table_agentstat_config, mongo_table_agentstat_config,
    sqlite3_agentstat_config, mysql_agentstat_config, postgresql_agentstat_config
):
    configs = {
        'inmemory_table': inmemory_table_agentstat_config, 
        'mongo': mongo_table_agentstat_config, 
        'sqlite3': sqlite3_agentstat_config, 
        'mysql': mysql_agentstat_config,
        'postgresql': postgresql_agentstat_config  
    }
    return configs