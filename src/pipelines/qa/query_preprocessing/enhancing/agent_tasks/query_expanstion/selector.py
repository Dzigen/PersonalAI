from .......utils import AgentTaskSolverConfig, Logger
from .general_parsers import qexpan_custom_formate, qexpan_custom_postprocess
from .v1 import QEXPAN_SUITE_V1

QEXPAN_LOG_PATH = "log/qa/query_preprocessing/enhancing/agent_tasks/query_expansion"

AVAILABLE_QEXPAN_TCONFIGS = {
    'v1': QEXPAN_SUITE_V1
}


class AgentQueryExpansionCheckConfigSelector:
    @staticmethod
    def get_available_configs():
        return AVAILABLE_QEXPAN_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v1', cache_table_name: str = "qp_qexpan_agent_task_cache") -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_QEXPAN_TCONFIGS[base_config_version],
            formate_context_func=qexpan_custom_formate, postprocess_answer_func=qexpan_custom_postprocess,
            cache_table_name=cache_table_name,
            log=Logger(QEXPAN_LOG_PATH))
