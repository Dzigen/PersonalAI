import pytest

from src.knowledge_graph_model import EmbeddingsModel, EmbeddingsModelConfig, GraphModel, GraphModelConfig
from src.db_drivers.vector_driver import VectorDBConnectionConfig, VectorDriver, VectorDriverConfig, VectorDBInstance
from src.db_drivers.vector_driver.embedders import EmbedderModel, EmbedderModelConfig
from src.db_drivers.graph_driver import GraphDriver, GraphDriverConfig, DEFAULT_NEO4J_CONFIG
from src.utils.data_structs import Triplet, TripletCreator, NodeCreator
from src.utils import Logger

@pytest.fixture
def embeddings_chroma_model():
    config = EmbeddingsModelConfig(
        nodesdb_driver_config=VectorDriverConfig(db_config=VectorDBConnectionConfig(
            path='./volumes/chroma', db_info={'db': 'testing', 'table': 'vectorized_nodes'}, need_to_clear=True)),
        tripletsdb_driver_config=VectorDriverConfig(db_config=VectorDBConnectionConfig(
            path='./volumes/chroma', db_info={'db': 'testing', 'table': 'vectorized_triplets'}, need_to_clear=True)),
        embedder_config=EmbedderModelConfig(model_name_or_path='../../models/intfloat/multilingual-e5-small', device='cuda'))
    return EmbeddingsModel(config)

@pytest.fixture
def graph_neo4j_model():
    config = GraphModelConfig(
        driver_config=GraphDriverConfig(
            db_vendor='neo4j',
            db_config=GraphDBConnectionConfig(
                uri="bolt://localhost:7687", db_info={'db': 'testing', 'table': 'testing'}
                params={'user': "neo4j", 'pwd': 'password'}, need_to_clear=True)))
    return GraphModel(config)

@pytest.fixture
def graph_inmemory_model():
    config = GraphModelConfig(
        driver_config=GraphDriverConfig(
            db_vendor='inmemory',
            db_config=GraphDBConnectionConfig(
                uri="", db_info={'db': 'testing', 'table': 'testing'}
                params={}, need_to_clear=True)))
    return GraphModel(config)
