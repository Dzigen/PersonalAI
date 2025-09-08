import pytest

import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.db_drivers.vector_driver import VectorDriverConfig, VectorDBConnectionConfig, EmbedderModelConfig
from src.db_drivers.graph_driver.configs import DEFAULT_INMEMORYGRAPH_CONFIG
from src.db_drivers.graph_driver import GraphDriverConfig
from src.kg_model import KnowledgeGraphModel, KnowledgeGraphModelConfig, GraphModelConfig, EmbeddingsModelConfig
from src.agents.configs import DEFAULT_STUBAGENT_CONFIG
from src.agents import AgentDriverConfig
from src.pipelines.memorize.updator import LLMUpdator, LLMUpdatorConfig

@pytest.fixture(scope='package')
def kg_model():
    graph_driver_config = GraphDriverConfig(
        db_vendor='inmemory_graph',
        db_config=DEFAULT_INMEMORYGRAPH_CONFIG)

    nodes_driver_config = VectorDriverConfig(
        db_vendor='chroma',
        db_config=VectorDBConnectionConfig(
            params={"hnsw:space": "ip", "hnsw:M": 4096},
            db_info={'db': 'test_db', 'table': "v_nodes"},
            conn={'path': './volumes/chroma'}))

    triplets_driver_config = VectorDriverConfig(
        db_vendor='chroma',
        db_config=VectorDBConnectionConfig(
            params={"hnsw:space": "ip", "hnsw:M": 4096},
            db_info={'db': 'test_db', 'table': "v_triplets"},
            conn={'path': './volumes/chroma'}))

    embedder_config = EmbedderModelConfig()

    kg_config = KnowledgeGraphModelConfig(
        graph_config=GraphModelConfig(driver_config=graph_driver_config),
        embeddings_config=EmbeddingsModelConfig(
            nodesdb_driver_config=nodes_driver_config,
            tripletsdb_driver_config=triplets_driver_config,
            embedder_config=embedder_config),
        nodestree_config=None  # TODO
    )

    return KnowledgeGraphModel(
        config=kg_config)


@pytest.fixture(scope='function')
def llm_updator(kg_model):
    updator_config = LLMUpdatorConfig(
        lang='en',
        adriver_config=AgentDriverConfig(
            name='stub', agent_config=DEFAULT_STUBAGENT_CONFIG)
    )
    return LLMUpdator(kg_model, updator_config)
