from ........utils import AgentTaskSolverConfig, Logger
from .general_parsers import kwe_custom_formate, kwe_custom_postprocess
from .v1 import KWE_GEN_SUITE_V1
from .v2 import KWE_GEN_SUITE_V2

KW_EXTRACTION_LOG_PATH = 'log/qa/kg_reasoner/weak/query_parser/agent_tasks/kw_extraction'

AVAILABLE_KWE_TCONFIGS = {
    'v1': KWE_GEN_SUITE_V1,
    'v2': KWE_GEN_SUITE_V2
}

class AgentKWETaskConfigSelector:
    @staticmethod
    def get_available_configs():
        return AVAILABLE_KWE_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v1') -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            suites=AVAILABLE_KWE_TCONFIGS[base_config_version],
            formate_context_func=kwe_custom_formate,
            postprocess_answer_func=kwe_custom_postprocess,
            log=Logger(KW_EXTRACTION_LOG_PATH))
