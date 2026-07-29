from .......utils import AgentTaskSolverConfig, BaseAgentTaskConfigSelector
from .......utils.logger import LogLevel
from .general_parsers import qd_custom_formate, qd_custom_postprocess
from .v1 import QD_SUITE_V1
from .v2 import QD_SUITE_V2
from .v3 import QD_SUITE_V3
from .v4 import QD_SUITE_V4

QD_LOG_PATH = "log/qa/query_preprocessing/decomposition/agent_tasks/query_decompsition"

AVAILABLE_QD_TCONFIGS = {
    'v1': QD_SUITE_V1,
    'v2': QD_SUITE_V2,
    'v3': QD_SUITE_V3,
    'v4': QD_SUITE_V4
}


class AgentQueryDecompTaskConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_QD_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v4',
               cache_table_name: str = "qp_qdecomp_agent_task_cache",
               inferencestat_table_name: str = "qp_qdecomp_agent_task_stat",
               verbose: bool = False, log_level: LogLevel = LogLevel.DISABLED) -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_QD_TCONFIGS[base_config_version],
            formate_context_func=qd_custom_formate, postprocess_answer_func=qd_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log_path=QD_LOG_PATH,
            verbose=verbose, log_level=log_level)
