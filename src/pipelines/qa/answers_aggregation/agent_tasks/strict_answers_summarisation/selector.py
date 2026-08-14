from ......utils import AgentTaskSolverConfig, BaseAgentTaskConfigSelector
from ......utils.logger import LogLevel
from .general_parsers import ssubasumm_custom_formate, ssubasumm_custom_postprocess
from .v1 import SSUBASUMM_SUITE_V1
from .v2 import SSUBASUMM_SUITE_V2
from .v3 import SSUBASUMM_SUITE_V3
from .v4 import SSUBASUMM_SUITE_V4

SSUBASUMM_LOG_PATH = "log/qa/answers_aggregation/agent_tasks/strict_answers_summarisation"

AVAILABLE_SSUBASUMM_TCONFIGS = {
    'v1': SSUBASUMM_SUITE_V1,
    'v2': SSUBASUMM_SUITE_V2,
    'v3': SSUBASUMM_SUITE_V3,
    'v4': SSUBASUMM_SUITE_V4
}


class AgentStrictSubASummTaskConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_SSUBASUMM_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v4',
               cache_table_name: str = "aagg_ssubasumm_agent_task_cache",
               inferencestat_table_name: str = "aagg_ssubasumm_agent_task_stat",
               verbose: bool = False, log_level: LogLevel = LogLevel.DISABLED) -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_SSUBASUMM_TCONFIGS[base_config_version],
            formate_context_func=ssubasumm_custom_formate, postprocess_answer_func=ssubasumm_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log_path=SSUBASUMM_LOG_PATH,
            verbose=verbose, log_level=log_level)
