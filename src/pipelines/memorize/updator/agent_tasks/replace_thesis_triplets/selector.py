from ......utils import AgentTaskSolverConfig, Logger
from .v1 import REPLACE_THESIS_TASK_CONFIGV1

REPLACE_THESIS_LOG_PATH = 'log/memorize/updator/agent_tasks/replace_thesis_triplets'

AVAILABLE_REPLACE_THESIS_TCONFIGS = {
    'v1': REPLACE_THESIS_TASK_CONFIGV1
}

class AgentReplThesisTripletTaskConfigSelector:
    @staticmethod
    def get_available_configs():
        return AVAILABLE_REPLACE_THESIS_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v1') -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            suites=AVAILABLE_REPLACE_THESIS_TCONFIGS[base_config_version]['suites'],
            formate_context_func=AVAILABLE_REPLACE_THESIS_TCONFIGS[base_config_version]['custom_formate'],
            log=Logger(REPLACE_THESIS_LOG_PATH))
