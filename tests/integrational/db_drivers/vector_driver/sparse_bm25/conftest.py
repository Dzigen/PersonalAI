import pytest
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.db_drivers.vector_driver import VectorDriver, VectorDriverConfig, VectorDBConnectionConfig

#!!!AVAILABLE VECTOR CONNECTIONS!!!#


@pytest.fixture(scope='package')
def opensearch_bm25_conn():
    config = VectorDriverConfig(
        db_vendor='opensearch', vector_category='sparse_bm25',
        db_config=VectorDBConnectionConfig(
            conn={'host': 'localhost', 'port': 9200, 'user': 'admin', 'pass': 'admin'}
        )
    )
    return VectorDriver.connect(config)

@pytest.fixture(scope='package')
def elasticsearch_bm25_conn():
    config = VectorDriverConfig(
        db_vendor='elasticsearch', vector_category='sparse_bm25',
        db_config=VectorDBConnectionConfig(
            conn={'host': 'localhost', 'port': 9201}
        )
    )
    return VectorDriver.connect(config)

@pytest.fixture(scope='package')
def weaviate_bm25_conn():
    config = VectorDriverConfig(
        db_vendor='weaviate', vector_category='sparse_bm25',
        db_config=VectorDBConnectionConfig(
            conn={'host': 'localhost', 'port': 8083}
        )
    )
    return VectorDriver.connect(config)

@pytest.fixture(scope='package')
def inmemory_bm25_conn():
    config = VectorDriverConfig(
        db_vendor='inmemory', vector_category='sparse_bm25',
        db_config=VectorDBConnectionConfig(
            params={
                'store_dump_name': 'inmemory_bm25',
                'load_from_disk': False,
                'load_dump_dir': f"{TEST_VOLUME_DIR}/inmemory_bm25",
                'save_on_disk': False,
                'save_dump_dir': f"{TEST_VOLUME_DIR}/inmemory_bm25"
            }
        ))
    return VectorDriver.connect(config)

# ------------------------------#

@pytest.fixture(scope='package')
def available_sparsebm25_connections(
        opensearch_bm25_conn, elasticsearch_bm25_conn, inmemory_bm25_conn, weaviate_bm25_conn):
    return {
        'opensearch': opensearch_bm25_conn,
        'elasticsearch': elasticsearch_bm25_conn,
        'weaviate': weaviate_bm25_conn,
        'inmemory': inmemory_bm25_conn
    }


@pytest.fixture(scope='function')
def bm25_conn(available_sparsebm25_connections, request):
    return available_sparsebm25_connections[request.param]
