from ......utils import AgentTaskSolverConfig, Logger
from .v2 import REPLACE_SIMPLE_TASK_CONFIGV2

REPLACE_SIMPLE_LOG_PATH = 'log/memorize/updator/agent_tasks/replace_simple_triplets'

AVAILABLE_REPLACE_SIMPLE_TCONFIGS = {
    'v1': ...,
    'v2': REPLACE_SIMPLE_TASK_CONFIGV2
}

class AgentReplSimpleTripletTaskConfigSelector:
    @staticmethod
    def get_available_configs():
        return AVAILABLE_REPLACE_SIMPLE_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v1') -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            suites=AVAILABLE_REPLACE_SIMPLE_TCONFIGS[base_config_version]['suites'],
            formate_context_func=AVAILABLE_REPLACE_SIMPLE_TCONFIGS[base_config_version]['custom_formate'],
            log=Logger(REPLACE_SIMPLE_LOG_PATH))
