import pytest
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from copy import deepcopy

from src.db_drivers.vector_driver import VectorDriverConfig, VectorDBConnectionConfig
from src.db_drivers.vector_driver.connectors.sparse.configs import DEFAULT_ELASTICSEARCH_BM25_CONFIG, \
    DEFAULT_INMEMORY_BM25_CONFIG, DEFAULT_OPENSEARCH_BM25_CONFIG, DEFAULT_WEAVIATE_BM25_CONFIG

@pytest.fixture(scope='session')
def opensearch_sparsebm25_config():
    config = VectorDriverConfig(
        db_vendor='opensearch', vector_category='sparse_bm25',
        db_config=deepcopy(DEFAULT_OPENSEARCH_BM25_CONFIG)
    )
    config.db_config.need_to_clear = True # !!! PAY ATTENTION !!!
    config.db_config.db_info['db'] = 'testing'
    config.db_config.db_info['table'] = 'testing'
    config.db_config.db_info['expected_db_base_path'] = TEST_VOLUME_DIR
    return config

@pytest.fixture(scope='session')
def elasticsearch_sparsebm25_config():
    config = VectorDriverConfig(
        db_vendor='elasticsearch', vector_category='sparse_bm25',
        db_config=deepcopy(DEFAULT_ELASTICSEARCH_BM25_CONFIG)
    )
    config.db_config.need_to_clear = True # !!! PAY ATTENTION !!!
    config.db_config.db_info['db'] = 'testing'
    config.db_config.db_info['table'] = 'testing'
    config.db_config.db_info['expected_db_base_path'] = TEST_VOLUME_DIR
    return config

@pytest.fixture(scope='session')
def weaviate_sparsebm25_config():
    config = VectorDriverConfig(
        db_vendor='weaviate', vector_category='sparse_bm25',
        db_config=deepcopy(DEFAULT_WEAVIATE_BM25_CONFIG)
    )
    config.db_config.need_to_clear = True # !!! PAY ATTENTION !!!
    config.db_config.db_info['db'] = 'testing'
    config.db_config.db_info['table'] = 'testing'
    config.db_config.db_info['expected_db_base_path'] = TEST_VOLUME_DIR
    return config

@pytest.fixture(scope='session')
def inmemory_sparsebm25_config():
    config = VectorDriverConfig(
        db_vendor='inmemory', vector_category='sparse_bm25',
        db_config=deepcopy(DEFAULT_INMEMORY_BM25_CONFIG)
    )
    config.db_config.need_to_clear = True # !!! PAY ATTENTION !!!
    config.db_config.db_info['db'] = 'testing'
    config.db_config.db_info['table'] = 'testing'
    config.db_config.db_info['expected_db_base_path'] = TEST_VOLUME_DIR
    return config

@pytest.fixture(scope='session')
def available_sparsebm25_vector_configs(
        opensearch_sparsebm25_config, elasticsearch_sparsebm25_config, 
        inmemory_sparsebm25_config, weaviate_sparsebm25_config):
    return {
        'opensearch': opensearch_sparsebm25_config,
        'elasticsearch': elasticsearch_sparsebm25_config,
        'weaviate': weaviate_sparsebm25_config,
        'inmemory': inmemory_sparsebm25_config
    }