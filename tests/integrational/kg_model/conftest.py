import pytest

from src.knowledge_graph_model import EmbeddingsModel, EmbeddingsModelConfig, GraphModel, GraphModelConfig
from src.db_drivers.vector_driver import VectorDBConnectionConfig, VectorDriver, VectorDriverConfig, VectorDBInstance
from src.db_drivers.vector_driver.embedders import EmbedderModel, EmbedderModelConfig
from src.db_drivers.graph_driver import GraphDriver, GraphDriverConfig, DEFAULT_NEO4J_CONFIG
from src.utils.data_structs import Triplet, TripletCreator, NodeCreator
from src.utils import Logger

# TODO
@pytest.fixture
def embeddings_model(db_vendor: str):
    config = EmbeddingsModelConfig(
        nodesdb_driver_config=VectorDriverConfig(db_config=VectorDBConnectionConfig(
            path='./tmp/nodes', db_name='vectorized_nodes', need_to_clear=True)),
        tripletsdb_driver_config=VectorDriverConfig(db_config=VectorDBConnectionConfig(
            path='./tmp_triplets', db_name='vectorized_triplets', need_to_clear=True)),
        embedder_config=EmbedderModelConfig(model_name_or_path='../../models/intfloat/multilingual-e5-small', device='cuda'))
    return EmbeddingsModel(config)


# TODO
@pytest.fixture
def graph_model(db_vendor: str):
    config = GraphModelConfig(
        driver_config=
    )
