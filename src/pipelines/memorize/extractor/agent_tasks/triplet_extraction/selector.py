from ......utils import AgentTaskSolverConfig, BaseAgentTaskConfigSelector
from ......utils.logger import LogLevel
from .general_parsers import etriplets_custom_postprocess, etriplets_custom_formate
from .v2 import TRIPLET_EXTRACT_SUITE_V2
from .v1 import TRIPLET_EXTRACT_SUITE_V1

TRIPLET_EXTR_LOG_PATH = 'log/memorize/extractor/agent_tasks/triplet_extraction'

AVAILABLE_TRIPLET_EXTRACT_TCONFIGS = {
    'v1': TRIPLET_EXTRACT_SUITE_V1,
    'v2': TRIPLET_EXTRACT_SUITE_V2
}


class AgentTripletExtrTaskConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_TRIPLET_EXTRACT_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v1',
               cache_table_name: str = "mem_agent_tripletextr_task_cache",
               inferencestat_table_name: str = "mem_agent_tripletextr_task_stat",
               verbose: bool = False, log_level: LogLevel = LogLevel.DISABLED) -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_TRIPLET_EXTRACT_TCONFIGS[base_config_version],
            formate_context_func=etriplets_custom_formate,
            postprocess_answer_func=etriplets_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log_path=TRIPLET_EXTR_LOG_PATH,
            verbose=verbose, log_level=log_level)
