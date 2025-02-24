from ......utils import AgentTaskSolverConfig, Logger
from .v2 import TRIPLET_EXTRACT_TASK_CONFIGV2
from .v1 import TRIPLET_EXTRACT_TASK_CONFIGV1

TRIPLET_EXTR_LOG_PATH = 'log/memorize/extractor/agent_tasks/triplet_extraction'

AVAILABLE_TRIPLET_EXTRACT_TCONFIGS = {
    'v1': TRIPLET_EXTRACT_TASK_CONFIGV1,
    'v2': TRIPLET_EXTRACT_TASK_CONFIGV2
}

class AgentTripletExtrTaskConfigSelector:
    @staticmethod
    def get_available_configs():
        return AVAILABLE_TRIPLET_EXTRACT_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v1') -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            suites=AVAILABLE_TRIPLET_EXTRACT_TCONFIGS[base_config_version]['suites'],
            formate_context_func=AVAILABLE_TRIPLET_EXTRACT_TCONFIGS[base_config_version]['custom_formate'],
            log=Logger(TRIPLET_EXTR_LOG_PATH))
