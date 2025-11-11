import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.db_drivers.graph_driver import GraphDriver, GraphDriverConfig, GraphDBConnectionConfig
from src.utils.data_structs import NodeType, RelationType
import pytest


#!!!AVAILABLE GRAPH CONNECTIONS!!!#


@pytest.fixture(scope='package')
def inmemory_graph_conn():
    config = GraphDriverConfig(
        db_vendor='inmemory_graph', db_config=GraphDBConnectionConfig(
        params={
            'load_dump_name': None,
            'load_from_disk': False,
            'load_dump_dir': f"{TEST_VOLUME_DIR}/inmemory_graph",
            'save_on_disk': True,
            'save_dump_dir': f"{TEST_VOLUME_DIR}/inmemory_graph"
        },
        db_info={'db': 'testing', 'table': 'testing'}, need_to_clear=True))
    return GraphDriver.connect(config)


@pytest.fixture(scope='package')
def neo4j_conn():
    config = GraphDriverConfig(
        db_vendor='neo4j', db_config=GraphDBConnectionConfig(
            # host: personalai_mmenschikov_test_neo4j
            host="localhost", port="7680", db_info={'db': 'testing', 'table': 'testing'},
            params={'user': "neo4j", 'pwd': 'password'}, need_to_clear=True))
    return GraphDriver.connect(config)


@pytest.fixture(scope='package')
def kuzu_conn():
    config = GraphDriverConfig(
        db_vendor='kuzu', db_config=GraphDBConnectionConfig(
            db_info={'db': 'testing', 'table': 'testing'},
            params={'path': f'{TEST_VOLUME_DIR}/kuzu', 'buffer_pool_size': 1024**3,
                    'table_type_map': {
                        'relations': {'forward': {RelationType.simple.value: 'simple', RelationType.hyper.value: 'hyper_rel', RelationType.episodic.value: 'episodic_rel', RelationType.time.value: 'time_rel'}, },
                        'nodes': {'forward': {NodeType.object.value: 'object', NodeType.hyper.value: 'hyper', NodeType.episodic.value: 'episodic', NodeType.time.value: 'time'}}}},
            need_to_clear=True))
    return GraphDriver.connect(config)

# ------------------------------#


@pytest.fixture(scope='package')
def available_graph_connections(
    inmemory_graph_conn,
    neo4j_conn,
    kuzu_conn
):
    return {
        'neo4j': neo4j_conn,
        'inmemory_graph': inmemory_graph_conn,
        'kuzu': kuzu_conn
    }


@pytest.fixture(scope='function')
def graphdb_conn(available_graph_connections, request):
    return available_graph_connections[request.param]
