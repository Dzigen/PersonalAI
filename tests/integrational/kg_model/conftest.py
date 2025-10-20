import pytest
from typing import Dict
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.db_drivers.vector_driver.embedders import EmbedderModelConfig
from src.kg_model.embeddings_model import EmbeddingsModelConfig
from src.kg_model.graph_model import GraphModelConfig
from src.kg_model import KnowledgeGraphModel, KnowledgeGraphModelConfig
from src.kg_model.utils import KGEmbeddersMapping

from .embeddings_model.conftest import available_embedding_configs, embeddings_chroma_config, embeddings_milvus_config
from .graph_model.conftest import available_graph_configs, graph_inmemory_config, graph_kuzu_config, graph_neo4j_config

# ------------------------------#

@pytest.fixture(scope='package')
def available_kg_models(
    available_embedding_configs: Dict[str, EmbeddingsModelConfig],
    available_graph_configs: Dict[str, GraphModelConfig]
    ):

    e5small_config = EmbedderModelConfig(model_name_or_path=f'{PROJECT_BASE_DIR}models/intfloat/multilingual-e5-small', device='cuda')
    embedders_map = KGEmbeddersMapping(
        embeddings_model={'nodes_dense': 'm-e5-small', 'triplets_dense': 'm-e5-small'},
        nodestree_model=None
    )
    embedders_configs = {'m-e5-small': e5small_config}

    kg_configs = {}
    for vector_name, vector_config in available_embedding_configs.items():
        for graph_name, graph_config in available_graph_configs.items():
            cur_config = KnowledgeGraphModelConfig(
                graph_struct_config=graph_config,
                graph_embeddings_config=vector_config,
                nodestree_config=None,
                embedders_configs=embedders_configs,
                embedders_map=embedders_map)
            kg_configs[f"{vector_name}/{graph_name}"] = KnowledgeGraphModel(
                cur_config)
    return kg_configs


@pytest.fixture(scope='function')
def kg_model(available_kg_models, request):
    return available_kg_models[request.param]
