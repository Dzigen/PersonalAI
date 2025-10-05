import pytest
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.db_drivers.vector_driver import VectorDriverConfig, VectorDBConnectionConfig, VectorComposer, VectorDBInstance
from src.utils.data_structs import create_id
from src.db_drivers.vector_driver.embedders import EmbedderModel, EmbedderModelConfig

FLOWERS_PASSAGES = ['Rose', 'Tulip', 'Lily', 'Daffodil', 'Daisy']
WANIMALS_PASSAGES = ['Lion', 'Tiger', 'Elephant', 'Giraffe', 'Zebra', 'Wild cat']
DANIMALS_PASSAGES = ['Dog', 'Cat', 'Horse', 'Cow', 'Sheep', 'Rabbit', 'Pig', 'Domestic wolf']
GNAMES_PASSAGES = ['Olivia', 'Amelia', 'Emma', 'Sophia', 'Mia']
BNAMES_PASSAGES = ['Noah', 'Liam', 'Oliver', 'Elijah', 'James']

PASSAGES = FLOWERS_PASSAGES + WANIMALS_PASSAGES + DANIMALS_PASSAGES + GNAMES_PASSAGES + BNAMES_PASSAGES

@pytest.fixture(scope='session')
def e5_small_embedder():
    config = EmbedderModelConfig(
        model_name_or_path=f'{PROJECT_BASE_DIR}models/intfloat/multilingual-e5-small',
        device='cuda'
    )
    return EmbedderModel(config)

@pytest.fixture(scope='session')
def vector_composer(e5_small_embedder):
    # dense
    chroma_dense_config = VectorDriverConfig(db_vendor='chroma', db_config=VectorDBConnectionConfig(
        conn={'path': f"{TEST_VOLUME_DIR}/chroma"}, db_info={'db': 'testing', 'table': 'testing'},
        params={"hnsw:space": "ip", "hnsw:M": 4096}, need_to_clear=True))

    milvus_dense_config = VectorDriverConfig(db_vendor='milvus', db_config=VectorDBConnectionConfig(
        conn={'host': 'localhost', 'port': 19520,
              'user': 'root', 'pass': 'Milvus'},
        db_info={'db': 'testing', 'table': 'testing'}, need_to_clear=True,
        params={'id_length': 32, 'vector_dim': 384, 'document_max_length': 51200,
                'load': True, 'flush': True, 'create_sleep': 1, 'search_metric': 'IP'}))

    # sparse
    opensearch_bm25_config = VectorDriverConfig(
        db_vendor='opensearch', vector_category='sparse_bm25',
        db_config=VectorDBConnectionConfig(
            conn={'host': 'localhost', 'port': 9200, 'user': 'admin', 'pass': 'admin'}))

    elasticsearch_bm25_config = VectorDriverConfig(
        db_vendor='elasticsearch', vector_category='sparse_bm25',
        db_config=VectorDBConnectionConfig(
            conn={'host': 'localhost', 'port': 9201}))

    inmemory_bm25_config = VectorDriverConfig(
        db_vendor='inmemory', vector_category='sparse_bm25',
        db_config=VectorDBConnectionConfig())

    vdb_config_mapping = {
        'dense_chroma': chroma_dense_config,
        'dense_milvus': milvus_dense_config,
        'bm25_opensearch': opensearch_bm25_config,
        'bm25_elasticsearch': elasticsearch_bm25_config,
        'bm25_inmemory': inmemory_bm25_config
    }

    emb_mapping = {
        'dense_chroma': e5_small_embedder,
        'dense_milvus': e5_small_embedder
    }

    composer = VectorComposer(vdb_config_mapping, emb_mapping)
    composer.clear()
    print("before: ",composer.count_items())

    items = [VectorDBInstance(id=create_id(text), document=text) for text in PASSAGES]
    composer.create(items=items)
    print("after: ", composer.count_items())
    composer.check_consistency()

    return composer
