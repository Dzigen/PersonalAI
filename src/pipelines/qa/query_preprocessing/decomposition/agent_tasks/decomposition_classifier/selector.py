from .......utils import AgentTaskSolverConfig, Logger
from .general_parsers import dc_custom_formate, dc_custom_postprocess
from .v1 import DECOMP_CLS_SUITE_V1

DECOMP_CLS_LOG_PATH = "log/qa/query_preprocessing/decomposition/agent_tasks/decompose_classifier"

AVAILABLE_DECOMPCLS_TCONFIGS = {
    'v1': DECOMP_CLS_SUITE_V1
}

class AgentDecompClsTaskConfigSelector:
    @staticmethod
    def get_available_configs():
        return AVAILABLE_DECOMPCLS_TCONFIGS

    @staticmethod
    def select(base_config_version:str = 'v1', cache_table_name:str="qa_agent_decompcls_task_cache") -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_DECOMPCLS_TCONFIGS[base_config_version],
            formate_context_func=dc_custom_formate, postprocess_answer_func=dc_custom_postprocess,
            cache_table_name=cache_table_name,
            log=Logger(DECOMP_CLS_LOG_PATH))