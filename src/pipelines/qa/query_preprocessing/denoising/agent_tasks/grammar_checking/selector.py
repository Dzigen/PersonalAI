from .......utils import AgentTaskSolverConfig, BaseAgentTaskConfigSelector
from .......utils.logger import LogLevel
from .general_parsers import gramcheck_custom_formate, gramcheck_custom_postprocess
from .v1 import GRAMCHECK_SUITE_V1
from .v2 import GRAMCHECK_SUITE_V2
from .v3 import GRAMCHECK_SUITE_V3
from .v4 import GRAMCHECK_SUITE_V4

GRAMCHECK_LOG_PATH = "log/qa/query_preprocessing/denoising/agent_tasks/grammar_check"

AVAILABLE_GRAMCHECK_TCONFIGS = {
    'v1': GRAMCHECK_SUITE_V1,
    'v2': GRAMCHECK_SUITE_V2,
    'v3': GRAMCHECK_SUITE_V3,
    'v4': GRAMCHECK_SUITE_V4
}


class AgentQueryGrammarCheckConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_GRAMCHECK_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v4',
               cache_table_name: str = "qp_gramcheck_agent_task_cache",
               inferencestat_table_name: str = "qp_gramcheck_agent_task_stat",
               verbose: bool = False, log_level: LogLevel = LogLevel.DISABLED) -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_GRAMCHECK_TCONFIGS[base_config_version],
            formate_context_func=gramcheck_custom_formate, postprocess_answer_func=gramcheck_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log_path=GRAMCHECK_LOG_PATH,
            verbose=verbose, log_level=log_level)
