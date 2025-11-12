import pytest
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.utils import AgentTaskSolver
from src.agents.connectors.StubAgentConnector import StubAgentConnector
from src.pipelines.memorize.updator.config import MEMUPDATOR_AGENTASKS_SELECTORS_MAPPING

@pytest.fixture(scope='package')
def replace_simple_agent_solver():
    atask_config = MEMUPDATOR_AGENTASKS_SELECTORS_MAPPING['replace_simple'].select(base_config_version='v1')
    return AgentTaskSolver(agent=StubAgentConnector(), config=atask_config)


@pytest.fixture(scope='package')
def replace_thesis_agent_solver():
    atask_config = MEMUPDATOR_AGENTASKS_SELECTORS_MAPPING['replace_thesis'].select(base_config_version='v1')
    return AgentTaskSolver(agent=StubAgentConnector(), config= atask_config)
