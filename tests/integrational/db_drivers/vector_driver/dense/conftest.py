import pytest
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from typing import Dict

from src.db_drivers.vector_driver import VectorDriver, VectorDriverConfig, VectorDBConnectionConfig
from src.db_drivers.vector_driver.utils import AbstractVectorDatabaseConnection
from .available_dense_vector_configs import chromadb_dense_config, inmemory_dense_config, elasticsearch_dense_config, \
    opensearch_dense_config, qdrant_dense_config, weaviate_dense_config, available_dense_vector_configs

@pytest.fixture(scope='package')
def available_dense_vector_connections(available_dense_vector_configs) -> Dict[str, AbstractVectorDatabaseConnection]:
    connections: Dict[str, AbstractVectorDatabaseConnection] = dict()
    for vendor_name, vendor_config in available_dense_vector_configs.items():
        connections[vendor_name] = VectorDriver.select(vendor_config)
        connections[vendor_name].open_connection()
    return connections

@pytest.fixture(scope='function')
def vectordb_dense_conn(available_dense_vector_connections, request):
    return available_dense_vector_connections[request.param]
