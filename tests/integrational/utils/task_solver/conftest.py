import pytest

import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
sys.path.insert(0, PROJECT_BASE_DIR)


from src.pipelines.qa.kg_reasoning.weak_reasoner.query_parser.utils import QueryLLMParserAgentTasksConfig
from src.pipelines.qa.kg_reasoning.weak_reasoner.answer_generator.utils import QALLMGeneratorAgentTasksConfig
from src.pipelines.memorize.updator.utils import MemUpdatorAgentTasksConfig
from src.pipelines.memorize.extractor.utils import MemExtractorAgentTasksConfig
from src.agents.connectors.StubAgentConnector import DEFAULT_STUBAGENT_CONFIG
from src.agents import AgentDriver, AgentDriverConfig
from src.utils import AgentTaskSolver

@pytest.fixture(scope='package')
def ag_solver():
    agent_conn = AgentDriver.connect(
        AgentDriverConfig(name='stub', agent_config=DEFAULT_STUBAGENT_CONFIG))
    task_config = QALLMGeneratorAgentTasksConfig()
    task_config.versions_to_configs()
    return AgentTaskSolver(agent_conn, task_config.ag)


@pytest.fixture(scope='package')
def ethesises_solver():
    agent_conn = AgentDriver.connect(
        AgentDriverConfig(name='stub', agent_config=DEFAULT_STUBAGENT_CONFIG))
    task_config = MemExtractorAgentTasksConfig()
    task_config.versions_to_configs()
    return AgentTaskSolver(agent_conn, task_config.thesises_extraction)


@pytest.fixture(scope='package')
def etriplets_solver():
    agent_conn = AgentDriver.connect(
        AgentDriverConfig(name='stub', agent_config=DEFAULT_STUBAGENT_CONFIG))
    task_config = MemExtractorAgentTasksConfig()
    task_config.versions_to_configs()
    return AgentTaskSolver(agent_conn, task_config.triplets_extraction)


@pytest.fixture(scope='package')
def kwe_solver():
    agent_conn = AgentDriver.connect(
        AgentDriverConfig(name='stub', agent_config=DEFAULT_STUBAGENT_CONFIG))
    task_config = QueryLLMParserAgentTasksConfig()
    task_config.versions_to_configs()
    return AgentTaskSolver(agent_conn, task_config.kw_extraction)


@pytest.fixture(scope='package')
def replace_simple_solver():
    agent_conn = AgentDriver.connect(
        AgentDriverConfig(name='stub', agent_config=DEFAULT_STUBAGENT_CONFIG))
    task_config = MemUpdatorAgentTasksConfig()
    task_config.versions_to_configs()
    return AgentTaskSolver(agent_conn, task_config.replace_simple)


@pytest.fixture(scope='package')
def replace_thesis_solver():
    agent_conn = AgentDriver.connect(
        AgentDriverConfig(name='stub', agent_config=DEFAULT_STUBAGENT_CONFIG))
    task_config = MemUpdatorAgentTasksConfig()
    task_config.versions_to_configs()
    return AgentTaskSolver(agent_conn, task_config.replace_thesis)
