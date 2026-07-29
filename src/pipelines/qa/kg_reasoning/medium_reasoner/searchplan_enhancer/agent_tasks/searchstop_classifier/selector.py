from ........utils import AgentTaskSolverConfig, BaseAgentTaskConfigSelector
from ........utils.logger import LogLevel
from .general_parsers import searchscls_custom_formate, searchscls_custom_postprocess
from .v1 import SEARCHSCLS_SUITE_V1
from .v2 import SEARCHSCLS_SUITE_V2
from .v3 import SEARCHSCLS_SUITE_V3
from .v4 import SEARCHSCLS_SUITE_V4

SEARCHSCLS_LOG_PATH = "log/qa/kg_reasoner/medium/plan_enhancer/agent_tasks/searchstop_classifier"

AVAILABLE_SEARCHSCLS_TCONFIGS = {
    'v1': SEARCHSCLS_SUITE_V1,
    'v2': SEARCHSCLS_SUITE_V2,
    'v3': SEARCHSCLS_SUITE_V3,
    'v4': SEARCHSCLS_SUITE_V4
}


class AgentSearchStopClassifierTaskConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_SEARCHSCLS_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v4',
               cache_table_name: str = "medreasn_searchscls_agent_task_cache",
               inferencestat_table_name: str = "medreasn_searchscls_agent_task_stat",
               verbose: bool = False, log_level: LogLevel = LogLevel.DISABLED) -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_SEARCHSCLS_TCONFIGS[base_config_version],
            formate_context_func=searchscls_custom_formate, postprocess_answer_func=searchscls_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log_path=SEARCHSCLS_LOG_PATH,
            verbose=verbose, log_level=log_level)
