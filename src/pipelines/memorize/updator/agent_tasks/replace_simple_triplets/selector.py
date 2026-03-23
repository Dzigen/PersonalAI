from ......utils import AgentTaskSolverConfig, BaseAgentTaskConfigSelector
from ......utils.logger import LogLevel
from .general_parsers import rs_custom_formate, rs_custom_postprocess
from .v1 import REPLACE_SIMPLE_SUITE_V1

REPLACE_SIMPLE_LOG_PATH = 'log/memorize/updator/agent_tasks/replace_simple_triplets'

AVAILABLE_REPLACE_SIMPLE_TCONFIGS = {
    'v1': REPLACE_SIMPLE_SUITE_V1
}


class AgentReplSimpleTripletTaskConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_REPLACE_SIMPLE_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v1',
               cache_table_name: str = "mem_agent_replsimple_task_cache",
               inferencestat_table_name: str = "mem_agent_replsimple_task_stat",
               verbose: bool = False, log_level: LogLevel = LogLevel.DISABLED) -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_REPLACE_SIMPLE_TCONFIGS[base_config_version],
            formate_context_func=rs_custom_formate, postprocess_answer_func=rs_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log_path=REPLACE_SIMPLE_LOG_PATH,
            verbose=verbose, log_level=log_level)
