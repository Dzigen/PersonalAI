from .......utils import AgentTaskSolverConfig, Logger
from .general_parsers import qd_custom_formate, qd_custom_postprocess
from .v1 import QUERY_DECOMP_SUITE_V1

QUERY_DECOMPOSITION_LOG_PATH = "log/qa/query_preprocessing/decomposition/agent_tasks/query_decompsition"

AVAILABLE_QDECOMP_TCONFIGS = {
    'v1': QUERY_DECOMP_SUITE_V1
}

class AgentQueryDecompTaskConfigSelector:
    @staticmethod
    def get_available_configs():
        return AVAILABLE_QDECOMP_TCONFIGS

    @staticmethod
    def select(base_config_version:str = 'v1', cache_table_name:str="qa_agent_qdecomp_task_cache") -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_QDECOMP_TCONFIGS[base_config_version],
            formate_context_func=qd_custom_formate, postprocess_answer_func=qd_custom_postprocess,
            cache_table_name=cache_table_name,
            log=Logger(QUERY_DECOMPOSITION_LOG_PATH))