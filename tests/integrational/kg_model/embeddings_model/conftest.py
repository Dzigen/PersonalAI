import pytest
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.db_drivers.vector_driver.embedders import EmbedderModelConfig
from src.db_drivers.vector_driver import VectorDBConnectionConfig, VectorDriverConfig
from src.kg_model import EmbeddingsModelConfig
from src.db_drivers.vector_driver.embedders import EmbedderModelConfig, EmbedderModel
from src.kg_model.embeddings_model import EmbeddingsModel

@pytest.fixture(scope='package')
def embeddings_chroma_config():
    config = EmbeddingsModelConfig(
        nodesdb_driver_configs_mapping={
            'nodes_dense': VectorDriverConfig(
                db_vendor='chroma', db_config=VectorDBConnectionConfig(
                    conn={'path': f'{TEST_VOLUME_DIR}/chroma'},
                    db_info={'db': 'testing', 'table': 'vectorized_nodes'},
                      params={"hnsw:space": "ip", "hnsw:M": 4096}, need_to_clear=True
                )
            )
        },
        tripletsdb_driver_configs_mapping={
            'triplets_dense': VectorDriverConfig(
                db_vendor='chroma', db_config=VectorDBConnectionConfig(
                    conn={'path': f'{TEST_VOLUME_DIR}/chroma'},
                    db_info={'db': 'testing', 'table': 'vectorized_triplets'},
                    params={"hnsw:space": "ip", "hnsw:M": 4096}, need_to_clear=True
                )
            )
        }
    )
    return config

# @pytest.fixture(scope='package')
# def embeddings_milvus_config():

#     config = EmbeddingsModelConfig(
#         nodesdb_driver_configs_mapping={
#             'nodes_dense': VectorDriverConfig(
#                 db_vendor='milvus', db_config=VectorDBConnectionConfig(
#                     conn={'host': 'localhost', 'port': 19520, 'user': 'root', 'pass': 'Milvus'},
#                     db_info={'db': 'testing', 'table': 'vectorized_nodes'}, need_to_clear=True,
#                     params={'id_length': 32, 'vector_dim': 384, 'document_max_length': 51200,
#                             'load': True, 'flush': True, 'create_sleep': 1, 'search_metric': 'IP'}
#                 )
#             )
#         },
#         tripletsdb_driver_configs_mapping={
#             'triplets_dense': VectorDriverConfig(
#                 db_vendor='milvus', db_config=VectorDBConnectionConfig(
#                     conn={'host': 'localhost', 'port': 19520, 'user': 'root', 'pass': 'Milvus'},
#                     db_info={'db': 'testing', 'table': 'vectorized_triplets'}, need_to_clear=True,
#                     params={'id_length': 32, 'vector_dim': 384, 'document_max_length': 51200,
#                             'load': True, 'flush': True, 'create_sleep': 1, 'search_metric': 'IP'}
#                 )
#             )
#         }
#     )

#     return config

@pytest.fixture(scope='package')
def embeddings_inmemory_config():
    config = EmbeddingsModelConfig(
        nodesdb_driver_configs_mapping={
            'nodes_dense': VectorDriverConfig(
                db_vendor='inmemory',
                db_config=VectorDBConnectionConfig(
                    db_info={'db': 'testing', 'table': 'vectorized_nodes'},
                    params={
                        'store_dump_name': 'inmemory_dense',
                        'load_from_disk': False,
                        'load_dump_dir': f"{TEST_VOLUME_DIR}/inmemory_dense",
                        'save_on_disk': False,
                        'save_dump_dir': f"{TEST_VOLUME_DIR}/inmemory_dense",
                        'vector_dim': 384
                    }
                )
            )
        },
        tripletsdb_driver_configs_mapping={
            'triplets_dense': VectorDriverConfig(
                db_vendor='inmemory',
                db_config=VectorDBConnectionConfig(
                    db_info={'db': 'testing', 'table': 'vectorized_triplets'},
                    params={
                        'store_dump_name': 'inmemory_dense',
                        'load_from_disk': False,
                        'load_dump_dir': f"{TEST_VOLUME_DIR}/inmemory_dense",
                        'save_on_disk': False,
                        'save_dump_dir': f"{TEST_VOLUME_DIR}/inmemory_dense",
                        'vector_dim': 384
                    }
                )
            )
        }
    )
    return config

@pytest.fixture(scope='package')
def embeddings_elasticsearch_config():
    config = EmbeddingsModelConfig(
        nodesdb_driver_configs_mapping={
            'nodes_dense': VectorDriverConfig(
                db_vendor='elasticsearch',
                db_config=VectorDBConnectionConfig(
                    db_info={'db': 'testing', 'table': 'vectorized_nodes'},
                    conn={'host': 'localhost', 'port': 9201}
                )
            )
        },
        tripletsdb_driver_configs_mapping={
            'triplets_dense': VectorDriverConfig(
                db_vendor='elasticsearch',
                db_config=VectorDBConnectionConfig(
                    db_info={'db': 'testing', 'table': 'vectorized_triplets'},
                    conn={'host': 'localhost', 'port': 9201}
                )
            )
        }
    )
    return config

@pytest.fixture(scope='package')
def embeddings_opensearch_config():
    config = EmbeddingsModelConfig(
        nodesdb_driver_configs_mapping={
            'nodes_dense': VectorDriverConfig(
                db_vendor='opensearch',
                db_config=VectorDBConnectionConfig(
                    conn={'host': 'localhost', 'port': 9200, 'user': 'admin', 'pass': 'admin'},
                    params={'vector_dim': 384, 'search_metric': 'innerproduct'}
                )
            )
        },
        tripletsdb_driver_configs_mapping={
            'triplets_dense': VectorDriverConfig(
                db_vendor='opensearch',
                db_config=VectorDBConnectionConfig(
                    conn={'host': 'localhost', 'port': 9200, 'user': 'admin', 'pass': 'admin'},
                    params={'vector_dim': 384, 'search_metric': 'innerproduct'}
                )
            )
        }
    )
    return config

@pytest.fixture(scope='package')
def embeddings_qdrant_config():
    config = EmbeddingsModelConfig(
        nodesdb_driver_configs_mapping={
            'nodes_dense': VectorDriverConfig(
                db_vendor='qdrant',
                db_config=VectorDBConnectionConfig(
                    conn={'host': 'localhost', 'port': 6333},
                    params={'vector_dim': 384, 'search_metric': 'Dot'}
                )
            )
        },
        tripletsdb_driver_configs_mapping={
            'triplets_dense': VectorDriverConfig(
                db_vendor='qdrant',
                db_config=VectorDBConnectionConfig(
                    conn={'host': 'localhost', 'port': 6333},
                    params={'vector_dim': 384, 'search_metric': 'Dot'}
                )
            )
        }
    )
    return config

# ------------------------------#

@pytest.fixture(scope='package')
def available_embedding_configs(
    embeddings_chroma_config, embeddings_inmemory_config, embeddings_elasticsearch_config,
    embeddings_opensearch_config, embeddings_qdrant_config, #embeddings_milvus_config
):
    return {
        'chroma': embeddings_chroma_config,
        #'milvus': embeddings_milvus_config,
        'inmemory': embeddings_inmemory_config,
        'elasticsearch': embeddings_elasticsearch_config,
        'opensearch': embeddings_opensearch_config,
        'qdrant': embeddings_qdrant_config
    }

@pytest.fixture(scope='module')
def available_embedding_models(available_embedding_configs):
    embedder_config = EmbedderModelConfig(model_name_or_path=f'{PROJECT_BASE_DIR}models/intfloat/multilingual-e5-small', device='cuda')
    embedder = EmbedderModel(embedder_config)
    embedders_configs = {'nodes_dense': embedder, 'triplets_dense': embedder}

    return {embedding_vendor: EmbeddingsModel(embedders_configs, config) for embedding_vendor, config in available_embedding_configs.items()}


@pytest.fixture(scope='function')
def embeddings_model(available_embedding_models, request):
    return available_embedding_models[request.param]
