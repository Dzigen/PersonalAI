from .......utils import AgentTaskSolverConfig, BaseAgentTaskConfigSelector
from .......utils.logger import LogLevel
from .general_parsers import qexpan_custom_formate, qexpan_custom_postprocess
from .v1 import QEXPAN_SUITE_V1
from .v2 import QEXPAN_SUITE_V2
from .v3 import QEXPAN_SUITE_V3

QEXPAN_LOG_PATH = "log/qa/query_preprocessing/enhancing/agent_tasks/query_expansion"

AVAILABLE_QEXPAN_TCONFIGS = {
    'v1': QEXPAN_SUITE_V1,
    'v2': QEXPAN_SUITE_V2,
    'v3': QEXPAN_SUITE_V3
}


class AgentQueryExpansionCheckConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_QEXPAN_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v3',
               cache_table_name: str = "qp_qexpan_agent_task_cache",
               inferencestat_table_name: str = "qp_qexpan_agent_task_stat",
               verbose: bool = False, log_level: LogLevel = LogLevel.DISABLED) -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_QEXPAN_TCONFIGS[base_config_version],
            formate_context_func=qexpan_custom_formate, postprocess_answer_func=qexpan_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log_path=QEXPAN_LOG_PATH,
            verbose=verbose, log_level=log_level)
