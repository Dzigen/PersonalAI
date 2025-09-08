from src.pipelines.qa.kg_reasoning.weak_reasoner.query_parser.configs import DEFAULT_KWE_TASK_CONFIG
from src.pipelines.qa.kg_reasoning.weak_reasoner.answer_generator.configs import DEFAULT_AG_TASK_CONFIG
from src.pipelines.memorize.updator.configs import DEFAULT_REPLACE_SIMPLE_TASK_CONFIG, DEFAULT_REPLACE_THESIS_TASK_CONFIG
from src.pipelines.memorize.extractor.configs import DEFAULT_THESISES_EXTR_TASK_CONFIG, DEFAULT_TRIPLETS_EXTR_TASK_CONFIG
from src.agents.connectors.StubAgentConnector import DEFAULT_STUBAGENT_CONFIG
from src.agents import AgentDriver, AgentDriverConfig
from src.utils import AgentTaskSolver
import pytest

import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
sys.path.insert(0, PROJECT_BASE_DIR)


@pytest.fixture(scope='package')
def ag_solver():
    agent_conn = AgentDriver.connect(
        AgentDriverConfig(name='stub', agent_config=DEFAULT_STUBAGENT_CONFIG))
    return AgentTaskSolver(agent_conn, DEFAULT_AG_TASK_CONFIG)


@pytest.fixture(scope='package')
def ethesises_solver():
    agent_conn = AgentDriver.connect(
        AgentDriverConfig(name='stub', agent_config=DEFAULT_STUBAGENT_CONFIG))
    return AgentTaskSolver(agent_conn, DEFAULT_THESISES_EXTR_TASK_CONFIG)


@pytest.fixture(scope='package')
def etriplets_solver():
    agent_conn = AgentDriver.connect(
        AgentDriverConfig(name='stub', agent_config=DEFAULT_STUBAGENT_CONFIG))
    return AgentTaskSolver(agent_conn, DEFAULT_TRIPLETS_EXTR_TASK_CONFIG)


@pytest.fixture(scope='package')
def kwe_solver():
    agent_conn = AgentDriver.connect(
        AgentDriverConfig(name='stub', agent_config=DEFAULT_STUBAGENT_CONFIG))
    return AgentTaskSolver(agent_conn, DEFAULT_KWE_TASK_CONFIG)


@pytest.fixture(scope='package')
def replace_simple_solver():
    agent_conn = AgentDriver.connect(
        AgentDriverConfig(name='stub', agent_config=DEFAULT_STUBAGENT_CONFIG))
    return AgentTaskSolver(agent_conn, DEFAULT_REPLACE_SIMPLE_TASK_CONFIG)


@pytest.fixture(scope='package')
def replace_thesis_solver():
    agent_conn = AgentDriver.connect(
        AgentDriverConfig(name='stub', agent_config=DEFAULT_STUBAGENT_CONFIG))
    return AgentTaskSolver(agent_conn, DEFAULT_REPLACE_THESIS_TASK_CONFIG)
