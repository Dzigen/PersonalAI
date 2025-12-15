from ....utils import AgentTaskSolverConfig
from src.utils import Logger
from src.dialogue_processing.utils import BaseAgentTaskConfigSelector
from .general_parsers import fct_preserv_custom_formate, fct_preserv_custom_postprocess
from .v1 import FACT_PRESERVE_SUITE_V1

FACT_PRESERVE_LOG_PATH = "log/dialogue_processing/fact_preserving/agent_tasks/fact_preserving"

AVAILABLE_FACT_PRESERVE_TCONFIGS = {
    'v1': FACT_PRESERVE_SUITE_V1,
}


class AgentFactPreservTaskConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_FACT_PRESERVE_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v1',
               cache_table_name: str = "fact_preserve_agent_task_cache",
               inferencestat_table_name: str = "fact_preserve_agent_task_stat") -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_FACT_PRESERVE_TCONFIGS[base_config_version],
            formate_context_func=fct_preserv_custom_formate, postprocess_answer_func=fct_preserv_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log=Logger(FACT_PRESERVE_LOG_PATH))
