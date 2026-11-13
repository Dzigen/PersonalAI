import sys
import pytest
from copy import deepcopy
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.db_drivers.graph_driver import GraphDriver, GraphDriverConfig, GraphDBConnectionConfig
from src.utils.data_structs import NodeType, RelationType
from src.db_drivers.graph_driver.connectors.configs import DEFAULT_BLAZEGRAPH_CONFIG, DEFAULT_FALKORDB_CONFIG, \
    DEFAULT_INMEMORYGRAPH_CONFIG, DEFAULT_KUZU_CONFIG, DEFAULT_NEO4J_CONFIG

@pytest.fixture(scope='session')
def inmemory_graph_config():
    config = GraphDriverConfig(
        db_vendor='inmemory_graph', 
        db_config=deepcopy(DEFAULT_INMEMORYGRAPH_CONFIG),
    )
    config.db_config.need_to_clear = True # !!! PAY ATTENTION !!!
    config.db_config.db_info['db'] = 'testing'
    config.db_config.db_info['table'] = 'testing'
    config.db_config.db_info['expected_db_base_path'] = TEST_VOLUME_DIR
    return config


@pytest.fixture(scope='session')
def neo4j_graph_config():
    config = GraphDriverConfig(
        db_vendor='neo4j', 
        db_config=deepcopy(DEFAULT_NEO4J_CONFIG)
    )
    config.db_config.need_to_clear = True # !!! PAY ATTENTION !!!
    config.db_config.db_info['db'] = 'testing'
    config.db_config.db_info['table'] = 'testing'
    config.db_config.db_info['expected_db_base_path'] = TEST_VOLUME_DIR
    return config


@pytest.fixture(scope='session')
def kuzu_graph_config():
    config = GraphDriverConfig(
        db_vendor='kuzu', 
        db_config=deepcopy(DEFAULT_KUZU_CONFIG)
    )
    config.db_config.need_to_clear = True # !!! PAY ATTENTION !!!
    config.db_config.db_info['db'] = 'testing'
    config.db_config.db_info['table'] = 'testing'
    config.db_config.db_info['expected_db_base_path'] = TEST_VOLUME_DIR
    return config


@pytest.fixture(scope='session')
def blazegraph_graph_config():
    config = GraphDriverConfig(
        db_vendor='blazegraph', 
        db_config=deepcopy(DEFAULT_BLAZEGRAPH_CONFIG)
    )
    config.db_config.need_to_clear = True # !!! PAY ATTENTION !!!
    config.db_config.db_info['db'] = 'testing'
    config.db_config.db_info['table'] = 'testing'
    config.db_config.db_info['expected_db_base_path'] = TEST_VOLUME_DIR
    return config

@pytest.fixture(scope='session')
def falkordb_graph_config():
    config = GraphDriverConfig(
        db_vendor='falkordb', 
        db_config=deepcopy(DEFAULT_FALKORDB_CONFIG)
    )
    config.db_config.need_to_clear = True # !!! PAY ATTENTION !!!
    config.db_config.db_info['db'] = 'testing'
    config.db_config.db_info['table'] = 'testing'
    config.db_config.db_info['expected_db_base_path'] = TEST_VOLUME_DIR
    return config

# ------------------------------#


@pytest.fixture(scope='session')
def available_graph_configs(
    inmemory_graph_config, neo4j_graph_config,
    kuzu_graph_config, blazegraph_graph_config,
    falkordb_graph_config
):
    return {
        'neo4j': neo4j_graph_config,
        'inmemory_graph': inmemory_graph_config,
        'kuzu': kuzu_graph_config,
        'blazegraph': blazegraph_graph_config,
        'falkordb': falkordb_graph_config
    }