import pytest

import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.db_drivers.vector_driver import VectorDriverConfig, VectorDBConnectionConfig, EmbedderModelConfig
from src.db_drivers.graph_driver import GraphDriverConfig, GraphDBConnectionConfig
from src.kg_model import KnowledgeGraphModel, KnowledgeGraphModelConfig, GraphModelConfig, EmbeddingsModelConfig
from src.agents.configs import DEFAULT_STUBAGENT_CONFIG
from src.agents import AgentDriverConfig, AgentDriver
from src.pipelines.memorize.updator import LLMUpdator, LLMUpdatorConfig
from src.utils.data_structs import RelationType, NodeType

@pytest.fixture(scope='package')
def kg_model():
    #
    graph_struct_config = GraphModelConfig(
        driver_config=GraphDriverConfig(
            db_vendor='kuzu',
            db_config=GraphDBConnectionConfig(
                db_info={'db': 'testing', 'table': 'testing'},
                params={'path': f'{TEST_VOLUME_DIR}/kuzu', 'buffer_pool_size': 1024**3,
                        'table_type_map': {
                            'relations': {'forward': {RelationType.simple.value: 'simple', RelationType.hyper.value: 'hyper_rel', RelationType.episodic.value: 'episodic_rel'}, },
                            'nodes': {'forward': {NodeType.object.value: 'object', NodeType.hyper.value: 'hyper', NodeType.episodic.value: 'episodic'}}
                        }
                },
                need_to_clear=True
            )
        )
    )

    #
    graph_embeddings_config = EmbeddingsModelConfig(
        nodesdb_driver_config=VectorDriverConfig(db_vendor='chroma', db_config=VectorDBConnectionConfig(
            conn={'path': f'{TEST_VOLUME_DIR}/chroma'}, db_info={'db': 'testing', 'table': 'vectorized_nodes'}, params={"hnsw:space": "ip", "hnsw:M": 4096}, need_to_clear=True)),
        tripletsdb_driver_config=VectorDriverConfig(db_vendor='chroma', db_config=VectorDBConnectionConfig(
            conn={'path': f'{TEST_VOLUME_DIR}/chroma'}, db_info={'db': 'testing', 'table': 'vectorized_triplets'}, params={"hnsw:space": "ip", "hnsw:M": 4096}, need_to_clear=True)))

    #
    e5small_config = EmbedderModelConfig(model_name_or_path=f'{PROJECT_BASE_DIR}models/intfloat/multilingual-e5-small', device='cuda')
    embedders_config = {'m-e5-small': e5small_config}
    embedders_map = {
        'KnowledgeGraphModel': {
            'EmbeddingsModel': 'm-e5-small',
        }
    }

    #
    stubagent_config = AgentDriverConfig(name='stub', agent_config=DEFAULT_STUBAGENT_CONFIG)
    agents_config = {'stub': stubagent_config}
    agents_map = {
        'MemPipeline': {'general': 'stub'}
    }

    kg_config = KnowledgeGraphModelConfig(
        graph_struct_config=graph_struct_config,
        graph_embeddings_config=graph_embeddings_config,
        nodestree_config=None,
        embedders_config=embedders_config,
        embedders_map=embedders_map,
        agents_config=agents_config,
        agents_map=agents_map
    )

    return KnowledgeGraphModel(
        config=kg_config)


@pytest.fixture(scope='function')
def llm_updator(kg_model):
    updator_config = LLMUpdatorConfig(lang='en')
    return LLMUpdator(kg_model, updator_config)
