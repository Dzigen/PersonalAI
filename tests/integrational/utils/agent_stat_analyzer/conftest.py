import pytest
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.db_drivers.table_driver import TableDriverConfig, TableDBConnectionConfig
from src.utils.agent_stat_analyzer.utils import LLMInferenceStat

from src.utils.agent_stat_analyzer import AgentStatAnalyzer, AgentStatAnalyzerConfig

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

@pytest.fixture(scope='package')
def inmemory_table_agentstat_config():
    inmemory_config = TableDBConnectionConfig(
        db_info={
            'db': 'test_db', 'table': 'test_table',
            'table_info': LLMInferenceStat
        },
        params={
            'tablestore_dump_name': 'inmemory_table_store',
            'load_from_disk': False,
            'max_storage': 5e+8,
            'load_dump_dir': f"{TEST_VOLUME_DIR}/inmemory_table",
            'save_on_disk': True,
            'save_dump_dir': f"{TEST_VOLUME_DIR}/inmemory_table"
        },
        need_to_clear=True)

    driver_config = TableDriverConfig(
        db_vendor='inmemory_table', db_config=inmemory_config)
    return AgentStatAnalyzerConfig(table_driver_config=driver_config)

@pytest.fixture(scope='package')
def mongo_table_agentstat_config():
    mongo_config = TableDBConnectionConfig(
        host='localhost', port=27010, db_info={
            'db': 'test_db', 'table': 'test_collection', 'table_info': LLMInferenceStat},
        params={'username': 'user', 'password': 'pass', 'max_storage': -1}, need_to_clear=True)

    driver_config = TableDriverConfig(
        db_vendor='mongo', db_config=mongo_config)
    return AgentStatAnalyzerConfig(table_driver_config=driver_config)

@pytest.fixture(scope='package')
def sqlite3_agentstat_config():

    sqlite3_config = TableDBConnectionConfig(
        db_info={
            'db': 'personalai_test', 'table': 'test_table',
            'table_info': LLMInferenceStat,
            'create_table_query': CREATE_TABLE_QUERY
        },
        params={
            'database_dname': f'{TEST_VOLUME_DIR}/sqlite3'
        },
        need_to_clear=True)

    driver_config = TableDriverConfig(
        db_vendor='sqlite3', db_config=sqlite3_config)
    return AgentStatAnalyzerConfig(table_driver_config=driver_config)

@pytest.fixture(scope='package')
def mysql_agentstat_config():
    mysql_config = TableDBConnectionConfig(
        host='localhost', port=3306, db_info={
            'db': 'personalai_test', 'table': 'test_table',
            'table_info': LLMInferenceStat, 'create_table_query': CREATE_TABLE_QUERY},
        params={'username': 'personalai', 'password': 'personalai'},
        need_to_clear=True)

    driver_config = TableDriverConfig(
        db_vendor='mysql', db_config=mysql_config)
    return AgentStatAnalyzerConfig(table_driver_config=driver_config)

@pytest.fixture(scope='package')
def postgresql_agentstat_config():

    postgresql_config = TableDBConnectionConfig(
        host='localhost', port=5432, db_info={
            'db': 'personalai_test', 'table': 'test_table',
            'table_info': LLMInferenceStat,
            'create_table_query': CREATE_TABLE_QUERY},
        params={'username': 'personalai', 'password': 'personalai'},
        need_to_clear=True)

    driver_config = TableDriverConfig(
        db_vendor='postgresql', db_config=postgresql_config)
    return AgentStatAnalyzerConfig(table_driver_config=driver_config)

# ------------------------------#

@pytest.fixture(scope='package')
def available_agentstats(
    inmemory_table_agentstat_config,
    sqlite3_agentstat_config,
    mongo_table_agentstat_config,
    mysql_agentstat_config,
    postgresql_agentstat_config
):

    return {
        'inmemory_table': AgentStatAnalyzer(inmemory_table_agentstat_config),
        'sqlite3': AgentStatAnalyzer(sqlite3_agentstat_config),
        'mongo': AgentStatAnalyzer(mongo_table_agentstat_config),
        'mysql': AgentStatAnalyzer(mysql_agentstat_config),
        'postgresql': AgentStatAnalyzer(postgresql_agentstat_config)
    }


@pytest.fixture(scope='function')
def agentstat_conn(available_agentstats, request):
    return available_agentstats[request.param]
