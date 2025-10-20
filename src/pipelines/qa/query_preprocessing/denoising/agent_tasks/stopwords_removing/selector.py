from .......utils import AgentTaskSolverConfig, Logger
from .general_parsers import swremv_custom_formate, swremv_custom_postprocess
from .v1 import SWREMV_SUITE_V1

SWREMV_LOG_PATH = "log/qa/query_preprocessing/denoising/agent_tasks/stopwords_removing"

AVAILABLE_SWREMV_TCONFIGS = {
    'v1': SWREMV_SUITE_V1
}


class AgentStopWordsRemovingTaskConfigSelector:
    @staticmethod
    def get_available_configs():
        return AVAILABLE_SWREMV_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v1',
               cache_table_name: str = "qp_swremv_agent_task_cache",
               inferencestat_table_name: str = "qp_swremv_agent_task_stat") -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_SWREMV_TCONFIGS[base_config_version],
            formate_context_func=swremv_custom_formate, postprocess_answer_func=swremv_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log=Logger(SWREMV_LOG_PATH))
