from .......utils import AgentTaskSolverConfig, Logger
from .general_parsers import gramcheck_custom_formate, gramcheck_custom_postprocess
from .v1 import GRAMCHECK_SUITE_V1

GRAMCHECK_LOG_PATH = "log/qa/query_preprocessing/denoising/agent_tasks/grammar_check"

AVAILABLE_GRAMCHECK_TCONFIGS = {
    'v1': GRAMCHECK_SUITE_V1
}


class AgentQueryGrammarCheckConfigSelector:
    @staticmethod
    def get_available_configs():
        return AVAILABLE_GRAMCHECK_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v1', cache_table_name: str = "qp_gramcheck_agent_task_cache") -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_GRAMCHECK_TCONFIGS[base_config_version],
            formate_context_func=gramcheck_custom_formate, postprocess_answer_func=gramcheck_custom_postprocess,
            cache_table_name=cache_table_name,
            log=Logger(GRAMCHECK_LOG_PATH))
