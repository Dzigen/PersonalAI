from .......utils import AgentTaskSolverConfig, BaseAgentTaskConfigSelector
from .......utils.logger import LogLevel
from .general_parsers import swremv_custom_formate, swremv_custom_postprocess
from .v1 import SWREMV_SUITE_V1
from .v2 import SWREMV_SUITE_V2

SWREMV_LOG_PATH = "log/qa/query_preprocessing/denoising/agent_tasks/stopwords_removing"

AVAILABLE_SWREMV_TCONFIGS = {
    'v1': SWREMV_SUITE_V1,
    'v2': SWREMV_SUITE_V2
}


class AgentStopWordsRemovingTaskConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_SWREMV_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v2',
               cache_table_name: str = "qp_swremv_agent_task_cache",
               inferencestat_table_name: str = "qp_swremv_agent_task_stat",
               verbose: bool = False, log_level: LogLevel = LogLevel.DISABLED) -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_SWREMV_TCONFIGS[base_config_version],
            formate_context_func=swremv_custom_formate, postprocess_answer_func=swremv_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log_path=SWREMV_LOG_PATH,
            verbose=verbose, log_level=log_level)
