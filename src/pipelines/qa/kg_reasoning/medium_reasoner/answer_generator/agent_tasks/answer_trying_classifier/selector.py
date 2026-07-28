from ........utils import AgentTaskSolverConfig, BaseAgentTaskConfigSelector
from ........utils.logger import LogLevel
from .general_parsers import answcls_custom_formate, answcls_custom_postprocess
from .v1 import ANSWCLS_SUITE_V1
from .v2 import ANSWCLS_SUITE_V2
from .v3 import ANSWCLS_SUITE_V3

ANSWCLS_LOG_PATH = "log/qa/kg_reasoner/medium/answer_generation//agent_tasks/answer_classifier"

AVAILABLE_ANSWCLS_TCONFIGS = {
    'v1': ANSWCLS_SUITE_V1,
    'v2': ANSWCLS_SUITE_V2,
    'v3': ANSWCLS_SUITE_V3
}


class AgentAnswerClassifierTaskConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_ANSWCLS_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v3',
               cache_table_name: str = "medreasn_answcls_agent_task_cache",
               inferencestat_table_name: str = "medreasn_answcls_agent_task_stat",
               verbose: bool = False, log_level: LogLevel = LogLevel.DISABLED) -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_ANSWCLS_TCONFIGS[base_config_version],
            formate_context_func=answcls_custom_formate, postprocess_answer_func=answcls_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log_path=ANSWCLS_LOG_PATH,
            verbose=verbose, log_level=log_level)
