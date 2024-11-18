import pytest

import sys
# TO CHANGE
PROJECT_BASE_DIR = '../../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.db_drivers.graph_driver import GraphDriver, GraphDriverConfig, GraphDBConnectionConfig

#!!!AVAILABLE GRAPH CONNECTIONS!!!#

@pytest.fixture(scope='package')
def inmemory_graph_conn():
    config = GraphDriverConfig(db_vendor='inmemory_graph', db_config=GraphDBConnectionConfig(
        db_info={'db': 'testing', 'table': 'testing'}, need_to_clear=True))
    return GraphDriver.connect(config)

@pytest.fixture(scope='package')
def neo4j_conn():
    config = GraphDriverConfig(db_vendor='neo4j', db_config=GraphDBConnectionConfig(
        uri="bolt://localhost:7687", db_info={'db': 'testing', 'table': 'testing'},
        params={'user': "neo4j", 'pwd': 'password'}, need_to_clear=True))
    return GraphDriver.connect(config)

#------------------------------#

@pytest.fixture(scope='package')
def available_graph_connections(
    inmemory_graph_conn,
    neo4j_conn
):
    return {
        'neo4j': neo4j_conn,
        'inmemory_graph': inmemory_graph_conn
    }

@pytest.fixture(scope='function')
def graphdb_conn(available_graph_connections, request):
    return available_graph_connections[request.param]
