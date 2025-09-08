from src.db_drivers.tree_driver.utils import TreeNodeType
from src.db_drivers.tree_driver import TreeDriver, TreeDriverConfig, TreeDBConnectionConfig
import pytest

import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)


#!!!AVAILABLE TREE CONNECTIONS!!!#


@pytest.fixture(scope='package')
def neo4j_conn():
    config = TreeDriverConfig(
        db_vendor='neo4j', db_config=TreeDBConnectionConfig(
            host="localhost", port="7680", db_info={'db': 'testingtree', 'table': 'testingtree'},
            params={'user': "neo4j", 'pwd': 'password'},
            need_to_clear=True))
    return TreeDriver.connect(config)


@pytest.fixture(scope='package')
def kuzu_conn():
    config = TreeDriverConfig(
        db_vendor='kuzu', db_config=TreeDBConnectionConfig(
            db_info={'db': 'testingtree', 'table': 'testingtree'},
            params={
                'path': f'{TEST_VOLUME_DIR}/kuzu', 'buffer_pool_size': 1024**3,
                'table_type_map': {'nodes': {'forward': {TreeNodeType.root.value: 'root', TreeNodeType.leaf.value: 'leaf', TreeNodeType.summarized.value: 'summarized'}}}},
            need_to_clear=False))
    return TreeDriver.connect(config)

# ------------------------------#


@pytest.fixture(scope='package')
def available_tree_connections(
    neo4j_conn,
    kuzu_conn
):
    return {
        'neo4j': neo4j_conn,
        'kuzu': kuzu_conn
    }


@pytest.fixture(scope='function')
def treedb_conn(available_tree_connections, request):
    return available_tree_connections[request.param]
