from ......utils import AgentTaskSolverConfig, Logger
from .v2 import TRIPLETS_EXTRACT_TASK_CONFIGV2

TRIPLETS_EXTR_LOG_PATH = 'log/memorize/extractor/weak/agent_tasks/triplet_extraction'

AVAILABLE_TRIPLETS_EXTRACT_TCONFIGS = {
    'v1': ...,
    'v2': TRIPLETS_EXTRACT_TASK_CONFIGV2
}

class AgentTripletsExtrTaskConfigSelector:
    @staticmethod
    def get_available_configs():
        return AVAILABLE_TRIPLETS_EXTRACT_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v1') -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            suites=AVAILABLE_TRIPLETS_EXTRACT_TCONFIGS[base_config_version]['suites'],
            formate_context_func=AVAILABLE_TRIPLETS_EXTRACT_TCONFIGS[base_config_version]['custom_formate'],
            log=Logger(TRIPLETS_EXTR_LOG_PATH))
