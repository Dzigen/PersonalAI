from ........utils import AgentTaskSolverConfig, Logger
from .v2 import AG_TASK_CONFIGV2

ANSWER_GENERATION_LOG_PATH = 'log/qa/kg_reasoner/weak/answer_generation/agent_tasks/ag'

AVAILABLE_AG_TCONFIGS = {
    'v1': ...,
    'v2': AG_TASK_CONFIGV2
}

class AgentAGTaskConfigSelector:
    @staticmethod
    def get_available_configs():
        return AVAILABLE_AG_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v1') -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            suites=AVAILABLE_AG_TCONFIGS[base_config_version]['suites'],
            formate_context_func=AVAILABLE_AG_TCONFIGS[base_config_version]['custom_formate'],
            log=Logger(ANSWER_GENERATION_LOG_PATH))
