import pytest
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.db_drivers.table_driver import TableDriver, TableDriverConfig, TableDBConnectionConfig
from src.utils.agent_stat_analyzer.utils import LLMInferenceStat

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
def inmemory_table_conn():
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
    return TableDriver.connect(driver_config)

@pytest.fixture(scope='package')
def mongo_table_conn():
    mongo_config = TableDBConnectionConfig(
        host='localhost', port=27010, db_info={
            'db': 'test_db', 'table': 'test_collection', 'table_info': LLMInferenceStat},
        params={'username': 'user', 'password': 'pass', 'max_storage': -1}, need_to_clear=True)

    driver_config = TableDriverConfig(
        db_vendor='mongo', db_config=mongo_config)
    return TableDriver.connect(driver_config)

@pytest.fixture(scope='package')
def sqlite3_conn():

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
    return TableDriver.connect(driver_config)

@pytest.fixture(scope='package')
def mysql_conn():
    mysql_config = TableDBConnectionConfig(
        host='localhost', port=3306, db_info={
            'db': 'personalai_test', 'table': 'test_table',
            'table_info': LLMInferenceStat, 'create_table_query': CREATE_TABLE_QUERY},
        params={'username': 'personalai', 'password': 'personalai'},
        need_to_clear=True)

    driver_config = TableDriverConfig(
        db_vendor='mysql', db_config=mysql_config)
    return TableDriver.connect(driver_config)

@pytest.fixture(scope='package')
def postgresql_conn():

    postgresql_config = TableDBConnectionConfig(
        host='localhost', port=5432, db_info={
            'db': 'personalai_test', 'table': 'test_table',
            'table_info': LLMInferenceStat,
            'create_table_query': CREATE_TABLE_QUERY},
        params={'username': 'personalai', 'password': 'personalai'},
        need_to_clear=True)

    driver_config = TableDriverConfig(
        db_vendor='postgresql', db_config=postgresql_config)
    return TableDriver.connect(driver_config)

# ------------------------------#

@pytest.fixture(scope='package')
def available_table_connections(
    inmemory_table_conn,
    sqlite3_conn,
    mongo_table_conn,
    mysql_conn,
    postgresql_conn
):
    return {
        'inmemory_table': inmemory_table_conn,
        'sqlite3': sqlite3_conn,
        'mongo': mongo_table_conn,
        'mysql': mysql_conn,
        'postgresql': postgresql_conn
    }


@pytest.fixture(scope='function')
def tabledb_conn(available_table_connections, request):
    return available_table_connections[request.param]
