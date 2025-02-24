from ......utils import AgentTaskSolverConfig, Logger
from .v2 import THESISES_EXTRACT_TASK_CONFIGV2

THESIS_EXTR_LOG_PATH = 'log/memorize/extractor/agent_tasks/thesis_extraction'

AVAILABLE_THESISES_EXTRACT_TCONFIGS = {
    'v1': ...,
    'v2': THESISES_EXTRACT_TASK_CONFIGV2
}

class AgentThesisesExtrTaskConfigSelector:
    @staticmethod
    def get_available_configs():
        return AVAILABLE_THESISES_EXTRACT_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v1') -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            suites=AVAILABLE_THESISES_EXTRACT_TCONFIGS[base_config_version]['suites'],
            formate_context_func=AVAILABLE_THESISES_EXTRACT_TCONFIGS[base_config_version]['custom_formate'],
            log=Logger(THESIS_EXTR_LOG_PATH))
