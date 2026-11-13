import pytest
import sys

from typing import Dict

# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.db_drivers.vector_driver import VectorDriver
from src.db_drivers.vector_driver.utils import AbstractVectorDatabaseConnection

from .available_sparse_vector_configs import opensearch_sparsebm25_config, elasticsearch_sparsebm25_config, \
    inmemory_sparsebm25_config, weaviate_sparsebm25_config, available_sparsebm25_vector_configs

@pytest.fixture(scope='package')
def available_sparsebm25_vector_connections(available_sparsebm25_vector_configs) -> Dict[str, AbstractVectorDatabaseConnection]:
    connections: Dict[str, AbstractVectorDatabaseConnection] = dict()
    for vendor_name, vendor_config in available_sparsebm25_vector_configs.items():
        connections[vendor_name] = VectorDriver.select(vendor_config)
        connections[vendor_name].open_connection()
    return connections


@pytest.fixture(scope='function')
def vectordb_sparsebm25_conn(available_sparsebm25_vector_connections, request):
    return available_sparsebm25_vector_connections[request.param]
