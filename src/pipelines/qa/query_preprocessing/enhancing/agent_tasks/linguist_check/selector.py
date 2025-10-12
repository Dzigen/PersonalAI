from .......utils import AgentTaskSolverConfig, Logger
from .general_parsers import lcheck_custom_formate, lcheck_custom_postprocess
from .v1 import LCHECK_SUITE_V1

LCHECK_LOG_PATH = "log/qa/query_preprocessing/enhancing/agent_tasks/linguist_checkk"

AVAILABLE_LCHECK_TCONFIGS = {
    'v1': LCHECK_SUITE_V1
}


class AgentQueryLinguistCheckConfigSelector:
    @staticmethod
    def get_available_configs():
        return AVAILABLE_LCHECK_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v1',
               cache_table_name: str = "qp_lcheck_agent_task_cache",
               inferencestat_table_name: str = "qp_lcheck_agent_task_stat") -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_LCHECK_TCONFIGS[base_config_version],
            formate_context_func=lcheck_custom_formate, postprocess_answer_func=lcheck_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log=Logger(LCHECK_LOG_PATH))
