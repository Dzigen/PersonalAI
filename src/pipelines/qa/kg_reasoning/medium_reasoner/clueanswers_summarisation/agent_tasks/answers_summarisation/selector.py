from ........utils import AgentTaskSolverConfig, BaseAgentTaskConfigSelector
from ........utils.logger import LogLevel
from .general_parsers import casumm_custom_formate, casumm_custom_postprocess
from .v1 import CASUMM_SUITE_V1
from .v2 import CASUMM_SUITE_V2
from .v3 import CASUMM_SUITE_V3

CASUMM_LOG_PATH = "log/qa/kg_reasoner/medium/clueanswers_summarisation/agent_tasks/answers_summarisation"

AVAILABLE_CASUMM_TCONFIGS = {
    'v1': CASUMM_SUITE_V1,
    'v2': CASUMM_SUITE_V2,
    'v3': CASUMM_SUITE_V3
}


class AgentClueAnswersSummTaskConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_CASUMM_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v3',
               cache_table_name: str = "medreasn_casumm_agent_task_cache",
               inferencestat_table_name: str = "medreasn_casumm_agent_task_stat",
               verbose: bool = False, log_level: LogLevel = LogLevel.DISABLED) -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_CASUMM_TCONFIGS[base_config_version],
            formate_context_func=casumm_custom_formate, postprocess_answer_func=casumm_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log_path=CASUMM_LOG_PATH,
            verbose=verbose, log_level=log_level)
