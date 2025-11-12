from ........utils import AgentTaskSolverConfig, Logger
from .......utils import BaseAgentTaskConfigSelector
from .general_parsers import kwe_custom_formate, kwe_custom_postprocess
from .v1 import KWE_SUITE_V1
from .v2 import KWE_SUITE_V2

KWE_LOG_PATH = 'log/qa/kg_reasoner/weak/query_parser/agent_tasks/kwe'

AVAILABLE_KWE_TCONFIGS = {
    'v1': KWE_SUITE_V1,
    'v2': KWE_SUITE_V2
}


class AgentKWETaskConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_KWE_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v2',
               cache_table_name: str = "qa_agent_kwe_task_cache",
               inferencestat_table_name: str = "qa_agent_kwe_task_stat") -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_KWE_TCONFIGS[base_config_version],
            formate_context_func=kwe_custom_formate, postprocess_answer_func=kwe_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log=Logger(KWE_LOG_PATH))
