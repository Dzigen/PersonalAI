import pytest
from typing import Dict
from copy import deepcopy
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.db_drivers.vector_driver.embedders import EmbedderModelConfig
from src.kg_model.embeddings_model import EmbeddingsModelConfig
from src.kg_model.graph_model import GraphModelConfig
from src.kg_model import KnowledgeGraphModelConfig
from src.kg_model.utils import KGEmbeddersMapping
from src.main import PersonalAI, PersonalAIConfig
from src.db_drivers.kv_driver import KVDBConnectionConfig, KeyValueDriverConfig

from ....integrational.kg_model.embeddings_model.conftest import available_embedding_configs, embeddings_chroma_config, embeddings_inmemory_config, \
    embeddings_elasticsearch_config, embeddings_qdrant_config, embeddings_weaviate_config, embeddings_opensearch_config
from ....integrational.kg_model.graph_model.conftest import available_graph_configs, graph_inmemory_config, graph_kuzu_config, \
    graph_neo4j_config, graph_blazegraph_config, graph_falkordb_config
from src.TextIdStore import TextIdStore, TextIdStoreConfig
from ....integrational.textid_store.conftest import available_textidstore_configs, redis_kvdriver_config, mongo_kvdriver_config, \
    inmemory_kvdriver_config, mixed_kvdriver_config, textidstore_instance

from .cases import AVAILABLE_GRAPH_MODELS, AVAILABLE_EMBEDDING_MODELS

# ------------------------------ #

@pytest.fixture(scope='module')
def available_kg_configs(
    available_embedding_configs: Dict[str, EmbeddingsModelConfig],
    available_graph_configs: Dict[str, GraphModelConfig]
    ):

    e5small_config = EmbedderModelConfig(model_name_or_path=f'{PROJECT_BASE_DIR}models/intfloat/multilingual-e5-small', device='cuda')
    embedders_map = KGEmbeddersMapping(
        embeddings_model={'dense_nodes': 'm-e5-small', 'dense_triplets': 'm-e5-small'},
        nodestree_model=None
    )
    embedders_configs = {'m-e5-small': e5small_config}

    kg_configs = {}
    for vector_name in AVAILABLE_EMBEDDING_MODELS:
        vector_config = available_embedding_configs[vector_name]

        for graph_name in AVAILABLE_GRAPH_MODELS:
            graph_config = available_graph_configs[graph_name]

            cur_config = KnowledgeGraphModelConfig(
                graph_struct_config=graph_config,
                graph_embeddings_config=vector_config,
                nodestree_config=None,
                embedders_configs=embedders_configs,
                embedders_map=embedders_map)
            kg_configs[f"{vector_name}/{graph_name}"] = cur_config

    return kg_configs


@pytest.fixture(scope='function')
def personalai_inst(available_kg_configs: Dict[str, KnowledgeGraphModelConfig], available_textidstore_configs: Dict[str, TextIdStoreConfig], request):
    kg_setting_name, kvstore_setting_name = request.param.split("|")
    pai_config = PersonalAIConfig(
        kg_model_config=available_kg_configs[kg_setting_name],
        textidstore_config=available_textidstore_configs[kvstore_setting_name]
    )


    pai_config.qa_pipeline_config.reasoner_config.reasoner_config.knowledge_comparator_config.reranker_driver_config.strategy_config.vdb_names = ['dense_nodes']
    pai_config.qa_pipeline_config.reasoner_config.reasoner_config.knowledge_retriever_config.filter_config.reranker_driver_config.strategy_config.vdb_names = ['dense_triplets']
    personalai = PersonalAI(config=pai_config)

    return personalai
