from ......utils import AgentTaskSolverConfig, BaseAgentTaskConfigSelector
from ......utils.logger import LogLevel
from .general_parsers import rt_custom_formate, rt_custom_postprocess
from .v1 import REPLACE_THESIS_SUITE_V1

REPLACE_THESIS_LOG_PATH = 'log/memorize/updator/agent_tasks/replace_thesis_triplets'

AVAILABLE_REPLACE_THESIS_TCONFIGS = {
    'v1': REPLACE_THESIS_SUITE_V1
}


class AgentReplThesisTripletTaskConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_REPLACE_THESIS_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v1',
               cache_table_name: str = "mem_agent_replthesis_task_cache",
               inferencestat_table_name: str = "mem_agent_replthesis_task_stat",
               verbose: bool = False, log_level: LogLevel = LogLevel.DISABLED) -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_REPLACE_THESIS_TCONFIGS[base_config_version],
            formate_context_func=rt_custom_formate, postprocess_answer_func=rt_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log_path=REPLACE_THESIS_LOG_PATH,
            verbose=verbose, log_level=log_level)
