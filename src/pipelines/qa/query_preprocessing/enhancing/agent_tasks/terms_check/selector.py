from .......utils import AgentTaskSolverConfig, BaseAgentTaskConfigSelector
from .......utils.logger import LogLevel
from .general_parsers import tcheck_custom_formate, tcheck_custom_postprocess
from .v1 import TCHECK_SUITE_V1
from .v2 import TCHECK_SUITE_V2
from .v3 import TCHECK_SUITE_V3
from .v4 import TCHECK_SUITE_V4
from .v5 import TCHECK_SUITE_V5

TCHECK_LOG_PATH = "log/qa/query_preprocessing/enhancing/agent_tasks/terms_check"

AVAILABLE_TCHECK_TCONFIGS = {
    'v1': TCHECK_SUITE_V1,
    'v2': TCHECK_SUITE_V2,
    'v3': TCHECK_SUITE_V3,
    'v4': TCHECK_SUITE_V4,
    'v5': TCHECK_SUITE_V5
}


class AgentQueryTermsCheckConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_TCHECK_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v5',
               cache_table_name: str = "qp_tcheck_agent_task_cache",
               inferencestat_table_name: str = "qp_tcheck_agent_task_stat",
               verbose: bool = False, log_level: LogLevel = LogLevel.DISABLED) -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_TCHECK_TCONFIGS[base_config_version],
            formate_context_func=tcheck_custom_formate, postprocess_answer_func=tcheck_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log_path=TCHECK_LOG_PATH,
            verbose=verbose, log_level=log_level)
