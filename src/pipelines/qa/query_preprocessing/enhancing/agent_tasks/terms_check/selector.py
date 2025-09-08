from .......utils import AgentTaskSolverConfig, Logger
from .general_parsers import tcheck_custom_formate, tcheck_custom_postprocess
from .v1 import TCHECK_SUITE_V1

TCHECK_LOG_PATH = "log/qa/query_preprocessing/enhancing/agent_tasks/terms_check"

AVAILABLE_TCHECK_TCONFIGS = {
    'v1': TCHECK_SUITE_V1
}


class AgentQueryTermsCheckConfigSelector:
    @staticmethod
    def get_available_configs():
        return AVAILABLE_TCHECK_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v1', cache_table_name: str = "qp_tcheck_agent_task_cache") -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_TCHECK_TCONFIGS[base_config_version],
            formate_context_func=tcheck_custom_formate, postprocess_answer_func=tcheck_custom_postprocess,
            cache_table_name=cache_table_name,
            log=Logger(TCHECK_LOG_PATH))
