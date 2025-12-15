from src.utils import AgentTaskSolverConfig
from src.utils import Logger
from src.dialogue_processing.utils import BaseAgentTaskConfigSelector
from .general_parsers import answ_rephrase_custom_formate, answ_rephrase_custom_postprocess
from .v1 import ANSW_REPH_SUITE_V1

ANSW_REPH_LOG_PATH = "log/question_answer_rephrasing/answer_processing/answ_rephraser/agent_tasks/quest_rephraser"

AVAILABLE_ANSW_REPH_TCONFIGS = {
    'v1': ANSW_REPH_SUITE_V1,
}


class AgentAnswRephTaskConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_ANSW_REPH_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v1',
               cache_table_name: str = "answ_rephrase_agent_task_cache",
               inferencestat_table_name: str = "answ_rephrase_agent_task_stat") -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_ANSW_REPH_TCONFIGS[base_config_version],
            formate_context_func=answ_rephrase_custom_formate, postprocess_answer_func=answ_rephrase_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log=Logger(ANSW_REPH_LOG_PATH))
