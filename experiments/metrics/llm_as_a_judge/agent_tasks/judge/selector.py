from .v1 import LLMJUDGE_SUITE_V1
from .general_parsers import llmjudge_custom_formate, llmjudge_custom_postprocess
from src.utils import AgentTaskSolverConfig, Logger
import sys
BASE_PATH = '../'  # TO CHANGE
sys.path.insert(0, BASE_PATH)


LLMJUDGE_LOG_PATH = 'log/qa_evaluation/agen_tasks/llm_as_a_judge'

AVAILABLE_LLMJUDGE_TCONFIGS = {
    'v1': LLMJUDGE_SUITE_V1,
}


class AgentLLMJudgeTaskConfigSelector:
    @staticmethod
    def get_available_configs():
        return AVAILABLE_LLMJUDGE_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v1', cache_table_name: str = "agent_llmjudge_task_cache",
               inferencestat_table_name: str = "agent_llmjudge_tas_stat") -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_LLMJUDGE_TCONFIGS[base_config_version],
            formate_context_func=llmjudge_custom_formate,
            postprocess_answer_func=llmjudge_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log=Logger(LLMJUDGE_LOG_PATH))
