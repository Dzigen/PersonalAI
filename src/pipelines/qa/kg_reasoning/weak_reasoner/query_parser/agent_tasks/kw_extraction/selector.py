from ........utils import AgentTaskSolverConfig, Logger
from .v1 import KWE_TASK_CONFIGV1
from .v2 import KWE_TASK_CONFIGV2

KW_EXTRACTION_LOG_PATH = 'log/qa/kg_reasoner/weak/query_parser/agent_tasks/kw_extraction'

AVAILABLE_KWE_TCONFIGS = {
    'v1': KWE_TASK_CONFIGV1,
    'v2': KWE_TASK_CONFIGV2
}

class AgentKWETaskConfigSelector:
    @staticmethod
    def get_available_configs():
        return AVAILABLE_KWE_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v1') -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            suites=AVAILABLE_KWE_TCONFIGS[base_config_version]['suites'],
            formate_context_func=AVAILABLE_KWE_TCONFIGS[base_config_version]['custom_formate'],
            log=Logger(KW_EXTRACTION_LOG_PATH))
