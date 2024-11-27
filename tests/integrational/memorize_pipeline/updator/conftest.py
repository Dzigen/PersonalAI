import pytest

import sys
# TO CHANGE
PROJECT_BASE_DIR = '../..'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.pipelines.memorize.updator import LLMUpdator, LLMUpdatorConfig
from src.agents import AgentDriverConfig
from src.agents.configs import DEFAULT_STUBAGENT_CONFIG

from src.kg_model import KnowledgeGraphModel, GraphModelConfig, EmbeddingsModelConfig

@pytest.fixture(scope='package')
def kg_model():
    return KnowledgeGraphModel(
        graph_config=GraphModelConfig(),
        embeddings_config=EmbeddingsModelConfig()
    )

@pytest.fixture(scope='function')
def llm_updator(kg_model):
    updator_config = LLMUpdatorConfig(
        agent_config=AgentDriverConfig(name='stub', agent_config=DEFAULT_STUBAGENT_CONFIG)
    )
    return LLMUpdator(kg_model, updator_config)
