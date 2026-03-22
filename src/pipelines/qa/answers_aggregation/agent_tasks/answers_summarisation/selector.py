from ......utils import AgentTaskSolverConfig, BaseAgentTaskConfigSelector
from ......utils.logger import LogLevel
from .general_parsers import subasumm_custom_formate, subasumm_custom_postprocess
from .v1 import SUBASUMM_SUITE_V1
from .v2 import SUBASUMM_SUITE_V2

SUBASUMM_LOG_PATH = "log/qa/answers_aggregation/agent_tasks/answers_summarisation"

AVAILABLE_SUBASUMM_TCONFIGS = {
    'v1': SUBASUMM_SUITE_V1,
    'v2': SUBASUMM_SUITE_V2
}


class AgentSubASummTaskConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_SUBASUMM_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v2',
               cache_table_name: str = "aagg_subasumm_agent_task_cache",
               inferencestat_table_name: str = "aagg_subasumm_agent_task_stat",
               verbose: bool = False, log_level: LogLevel = LogLevel.DISABLED) -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_SUBASUMM_TCONFIGS[base_config_version],
            formate_context_func=subasumm_custom_formate, postprocess_answer_func=subasumm_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log_path=SUBASUMM_LOG_PATH,
            verbose=verbose, log_level=log_level)
