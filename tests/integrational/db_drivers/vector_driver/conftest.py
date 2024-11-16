import pytest

import sys
# TO CHANGE
PROJECT_BASE_DIR = '/home/dzigen/Desktop/PersonalAI/Personal-AI'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.db_drivers.vector_driver import VectorDriver, VectorDriverConfig, VectorDBConnectionConfig

#!!!AVAILABLE VECTOR CONNECTIONS!!!#

@pytest.fixture(scope='package')
def chromadb_conn():
    config = VectorDriverConfig(db_vendor='chroma', db_config=VectorDBConnectionConfig(
            path=f"{TEST_VOLUME_DIR}/chroma", db_info={'db':'testing', 'table': 'testing'}, need_to_clear=True))
    return VectorDriver.connect(config)

#------------------------------#

@pytest.fixture(scope='package')
def available_vector_connections(
    chromadb_conn
):
    return {
        'chroma': chromadb_conn
    }

@pytest.fixture(scope='function')
def vectordb_conn(available_vector_connections, request):
    return available_vector_connections[request.param]
