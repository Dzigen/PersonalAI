from .v1 import LLMJUDGE_SUITE_V1
from .general_parsers import llmjudge_custom_formate, llmjudge_custom_postprocess
from ....utils.task_solver import AgentTaskSolverConfig, BaseAgentTaskConfigSelector
from ....utils.logger import LogLevel

LLMJUDGE_LOG_PATH = 'log/qa_evaluation/agen_tasks/llm_as_a_judge'

AVAILABLE_LLMJUDGE_TCONFIGS = {
    'v1': LLMJUDGE_SUITE_V1,
}


class AgentLLMJudgeTaskConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_LLMJUDGE_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v1', cache_table_name: str = "agent_llmjudge_task_cache",
               inferencestat_table_name: str = "agent_llmjudge_tas_stat",
               verbose: bool = False, log_level: LogLevel = LogLevel.DISABLED, 
               log_base_path: str = '.') -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_LLMJUDGE_TCONFIGS[base_config_version],
            formate_context_func=llmjudge_custom_formate,
            postprocess_answer_func=llmjudge_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log_base_path=log_base_path, 
            log_relative_path=LLMJUDGE_LOG_PATH,
            verbose=verbose, log_level=log_level)
