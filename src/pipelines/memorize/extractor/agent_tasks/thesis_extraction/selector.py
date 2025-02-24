from ......utils import AgentTaskSolverConfig, Logger
from .v1 import THESIS_EXTRACT_TASK_CONFIGV1
from .v2 import THESIS_EXTRACT_TASK_CONFIGV2

THESIS_EXTR_LOG_PATH = 'log/memorize/extractor/agent_tasks/thesis_extraction'

AVAILABLE_THESIS_EXTRACT_TCONFIGS = {
    'v1': THESIS_EXTRACT_TASK_CONFIGV1,
    'v2': THESIS_EXTRACT_TASK_CONFIGV2
}

class AgentThesisExtrTaskConfigSelector:
    @staticmethod
    def get_available_configs():
        return AVAILABLE_THESIS_EXTRACT_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v1') -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            suites=AVAILABLE_THESIS_EXTRACT_TCONFIGS[base_config_version]['suites'],
            formate_context_func=AVAILABLE_THESIS_EXTRACT_TCONFIGS[base_config_version]['custom_formate'],
            log=Logger(THESIS_EXTR_LOG_PATH))
