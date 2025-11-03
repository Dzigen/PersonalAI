from ........utils import AgentTaskSolverConfig, Logger
from .......utils import BaseAgentTaskConfigSelector
from .general_parsers import answgen_custom_formate, answgen_custom_postprocess
from .v1 import ANSWGEN_SUITE_V1

ANSWGEN_LOG_PATH = "log/qa/kg_reasoner/medium/answer_generation/agent_tasks/answer_generator"

AVAILABLE_ANSWGEN_TCONFIGS = {
    'v1': ANSWGEN_SUITE_V1
}


class AgentAnswerGeneratorTaskConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_ANSWGEN_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v1',
               cache_table_name: str = "medreasn_answgen_agent_task_cache",
               inferencestat_table_name: str = "medreasn_answgen_agent_task_stat") -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_ANSWGEN_TCONFIGS[base_config_version],
            formate_context_func=answgen_custom_formate, postprocess_answer_func=answgen_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log=Logger(ANSWGEN_LOG_PATH))
