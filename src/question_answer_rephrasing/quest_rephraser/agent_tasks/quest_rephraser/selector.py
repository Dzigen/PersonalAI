from src.utils import AgentTaskSolverConfig
from src.utils import Logger
from src.dialogue_processing.utils import BaseAgentTaskConfigSelector
from .general_parsers import quest_rephrase_custom_formate, quest_rephrase_custom_postprocess
from .v1 import QUEST_REPH_SUITE_V1

QUEST_REPH_LOG_PATH = "log/question_answer_rephrasing/quest_rephraser/agent_tasks/quest_rephraser"

AVAILABLE_QUEST_REPH_TCONFIGS = {
    'v1': QUEST_REPH_SUITE_V1,
}


class AgentQuestRephTaskConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_QUEST_REPH_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v1',
               cache_table_name: str = "quest_rephrase_agent_task_cache",
               inferencestat_table_name: str = "quest_rephrase_agent_task_stat") -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_QUEST_REPH_TCONFIGS[base_config_version],
            formate_context_func=quest_rephrase_custom_formate, postprocess_answer_func=quest_rephrase_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log=Logger(QUEST_REPH_LOG_PATH))
