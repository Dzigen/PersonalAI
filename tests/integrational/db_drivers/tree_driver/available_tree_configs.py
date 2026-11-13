import pytest
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
sys.path.insert(0, PROJECT_BASE_DIR)
TEST_VOLUME_DIR = './volumes'

from src.db_drivers.tree_driver import TreeDriverConfig
from src.db_drivers.tree_driver.configs import DEFAULT_KUZUTREE_CONFIG, \
    DEFAULT_NEO4JTREE_CONFIG


@pytest.fixture(scope='session')
def neo4j_tree_config():
    config = TreeDriverConfig(
        db_vendor='neo4j', 
        db_config=DEFAULT_NEO4JTREE_CONFIG
    )
    config.db_config.need_to_clear = True # !!! PAY ATTENTION !!!
    config.db_config.db_info['db'] = 'testing'
    config.db_config.db_info['table'] = 'testing'
    config.db_config.db_info['expected_db_base_path'] = TEST_VOLUME_DIR
    return config


@pytest.fixture(scope='session')
def kuzu_tree_config():
    config = TreeDriverConfig(
        db_vendor='kuzu',
        db_config=DEFAULT_KUZUTREE_CONFIG
    )
    config.db_config.need_to_clear = True # !!! PAY ATTENTION !!!
    config.db_config.db_info['db'] = 'testing'
    config.db_config.db_info['table'] = 'testing'
    config.db_config.db_info['expected_db_base_path'] = TEST_VOLUME_DIR
    return config

# ------------------------------#

@pytest.fixture(scope='session')
def available_tree_configs(
    neo4j_tree_config,
    kuzu_tree_config
):
    return {
        'neo4j': neo4j_tree_config,
        'kuzu': kuzu_tree_config
    }