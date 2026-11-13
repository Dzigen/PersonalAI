import pytest
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from copy import deepcopy

from src.db_drivers.vector_driver import VectorDriver, VectorDriverConfig, VectorDBConnectionConfig
from src.db_drivers.vector_driver.connectors.dense.configs import DEFAULT_CHROMA_CONFIG, \
    DEFAULT_ELASTICSEARCH_CONFIG, DEFAULT_INMEMORY_CONFIG, DEFAULT_MILVUS_CONFIG, \
        DEFAULT_OPENSEARCH_CONFIG, DEFAULT_QDRANT_CONFIG, DEFAULT_WEAVIATE_CONFIG


@pytest.fixture(scope='session')
def chromadb_dense_config():
    config = VectorDriverConfig(
        db_vendor='chroma', 
        db_config=deepcopy(DEFAULT_CHROMA_CONFIG)
    )
    config.db_config.need_to_clear = True # !!! PAY ATTENTION !!!
    config.db_config.db_info['db'] = 'testing'
    config.db_config.db_info['table'] = 'testing'
    config.db_config.db_info['expected_db_base_path'] = TEST_VOLUME_DIR
    return config

@pytest.fixture(scope='session')
def inmemory_dense_config():
    config = VectorDriverConfig(
        db_vendor='inmemory', 
        db_config=deepcopy(DEFAULT_INMEMORY_CONFIG)
    )
    config.db_config.need_to_clear = True # !!! PAY ATTENTION !!!
    config.db_config.db_info['db'] = 'testing'
    config.db_config.db_info['table'] = 'testing'
    config.db_config.db_info['expected_db_base_path'] = TEST_VOLUME_DIR
    config.db_config.params['vector_dim'] = 130 # !!! PAY ATTENTION !!!
    return config

@pytest.fixture(scope='session')
def elasticsearch_dense_config():
    config = VectorDriverConfig(
        db_vendor='elasticsearch',
        db_config=deepcopy(DEFAULT_ELASTICSEARCH_CONFIG)
    )
    config.db_config.need_to_clear = True # !!! PAY ATTENTION !!!
    config.db_config.db_info['db'] = 'testing'
    config.db_config.db_info['table'] = 'testing'
    config.db_config.db_info['expected_db_base_path'] = TEST_VOLUME_DIR
    return config

@pytest.fixture(scope='session')
def opensearch_dense_config():
    config = VectorDriverConfig(
        db_vendor='opensearch',
        db_config=deepcopy(DEFAULT_OPENSEARCH_CONFIG)
    )
    config.db_config.need_to_clear = True # !!! PAY ATTENTION !!!
    config.db_config.db_info['db'] = 'testing'
    config.db_config.db_info['table'] = 'testing'
    config.db_config.db_info['expected_db_base_path'] = TEST_VOLUME_DIR
    config.db_config.params['vector_dim'] = 130 # !!! PAY ATTENTION !!!
    return config

@pytest.fixture(scope='session')
def qdrant_dense_config():
    config = VectorDriverConfig(
        db_vendor='qdrant',
        db_config=deepcopy(DEFAULT_QDRANT_CONFIG)
    )
    config.db_config.need_to_clear = True # !!! PAY ATTENTION !!!
    config.db_config.db_info['db'] = 'testing'
    config.db_config.db_info['table'] = 'testing'
    config.db_config.db_info['expected_db_base_path'] = TEST_VOLUME_DIR
    config.db_config.params['vector_dim'] = 130 # !!! PAY ATTENTION !!!
    return config

@pytest.fixture(scope='session')
def weaviate_dense_config():
    config = VectorDriverConfig(
        db_vendor='weaviate',
        db_config=deepcopy(DEFAULT_WEAVIATE_CONFIG)
    )
    config.db_config.need_to_clear = True # !!! PAY ATTENTION !!!
    config.db_config.db_info['db'] = 'testing'
    config.db_config.db_info['table'] = 'testing'
    config.db_config.db_info['expected_db_base_path'] = TEST_VOLUME_DIR
    return config

@pytest.fixture(scope='session')
def available_dense_vector_configs(
        chromadb_dense_config, inmemory_dense_config, elasticsearch_dense_config, opensearch_dense_config, qdrant_dense_config, weaviate_dense_config
    ):
    return {
        'chroma': chromadb_dense_config,
        'inmemory': inmemory_dense_config,
        'elasticsearch': elasticsearch_dense_config,
        'opensearch': opensearch_dense_config,
        'qdrant': qdrant_dense_config,
        'weaviate': weaviate_dense_config
    }