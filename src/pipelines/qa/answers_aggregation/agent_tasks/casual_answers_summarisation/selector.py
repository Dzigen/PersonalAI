from ......utils import AgentTaskSolverConfig, BaseAgentTaskConfigSelector
from ......utils.logger import LogLevel
from .general_parsers import csubasumm_custom_formate, csubasumm_custom_postprocess
from .v1 import CSUBASUMM_SUITE_V1

CSUBASUMM_LOG_PATH = "log/qa/answers_aggregation/agent_tasks/casual_answers_summarisation"

AVAILABLE_CSUBASUMM_TCONFIGS = {
    'v1': CSUBASUMM_SUITE_V1
}


class AgentCasualSubASummTaskConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_CSUBASUMM_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v1',
               cache_table_name: str = "aagg_csubasumm_agent_task_cache",
               inferencestat_table_name: str = "aagg_csubasumm_agent_task_stat",
               verbose: bool = False, log_level: LogLevel = LogLevel.DISABLED) -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_CSUBASUMM_TCONFIGS[base_config_version],
            formate_context_func=csubasumm_custom_formate, postprocess_answer_func=csubasumm_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log_path=CSUBASUMM_LOG_PATH,
            verbose=verbose, log_level=log_level)
