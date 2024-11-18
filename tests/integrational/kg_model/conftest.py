import pytest

import sys
# TO CHANGE
PROJECT_BASE_DIR = '../../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)


from src.knowledge_graph_model import EmbeddingsModel, EmbeddingsModelConfig, GraphModel, GraphModelConfig
from src.db_drivers.vector_driver import VectorDBConnectionConfig, VectorDriverConfig
from src.db_drivers.vector_driver.embedders import EmbedderModelConfig
from src.db_drivers.graph_driver import GraphDriverConfig, GraphDBConnectionConfig

#!!!AVAILABLE GRAPH MODELS!!!#

@pytest.fixture(scope='package')
def graph_neo4j_model():
    config = GraphModelConfig(
        driver_config=GraphDriverConfig(
            db_vendor='neo4j',
            db_config=GraphDBConnectionConfig(
                uri="bolt://localhost:7687", db_info={'db': 'testing', 'table': 'testing'},
                params={'user': "neo4j", 'pwd': 'password'}, need_to_clear=True)))
    return GraphModel(config)

@pytest.fixture(scope='package')
def graph_inmemory_model():
    config = GraphModelConfig(
        driver_config=GraphDriverConfig(
            db_vendor='inmemory_graph',
            db_config=GraphDBConnectionConfig(
                uri="", db_info={'db': 'testing', 'table': 'testing'},
                params=dict(), need_to_clear=True)))
    return GraphModel(config)

#------------------------------#

@pytest.fixture(scope='package')
def available_graph_models(
    graph_neo4j_model,
    graph_inmemory_model
):
    return {
        'neo4j': graph_neo4j_model,
        'inmemory_graph': graph_inmemory_model
    }

@pytest.fixture(scope='function')
def graph_model(available_graph_models, request):
    return available_graph_models[request.param]

#!!!AVAILABLE VECTOR MODELS!!!#

@pytest.fixture(scope='package')
def embeddings_chroma_model():
    config = EmbeddingsModelConfig(
        nodesdb_driver_config=VectorDriverConfig(db_config=VectorDBConnectionConfig(
            path=f'{TEST_VOLUME_DIR}/chroma', db_info={'db': 'testing', 'table': 'vectorized_nodes'}, need_to_clear=True)),
        tripletsdb_driver_config=VectorDriverConfig(db_config=VectorDBConnectionConfig(
            path=f'{TEST_VOLUME_DIR}/chroma', db_info={'db': 'testing', 'table': 'vectorized_triplets'}, need_to_clear=True)),
        embedder_config=EmbedderModelConfig(model_name_or_path=f'{PROJECT_BASE_DIR}/models/intfloat/multilingual-e5-small', device='cuda'))
    return EmbeddingsModel(config)

#------------------------------#

@pytest.fixture(scope='package')
def available_embedding_models(
    embeddings_chroma_model,
):
    return {
        'chroma': embeddings_chroma_model
    }

@pytest.fixture(scope='function')
def embeddings_model(available_embedding_models, request):
    return available_embedding_models[request.param]
