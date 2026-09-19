from .......utils import AgentTaskSolverConfig, BaseAgentTaskConfigSelector
from .......utils.logger import LogLevel
from .general_parsers import dc_custom_formate, dc_custom_postprocess
from .v1 import DC_SUITE_V1
from .v2 import DC_SUITE_V2
from .v3 import DC_SUITE_V3
from .v4 import DC_SUITE_V4

DC_LOG_PATH = "log/qa/query_preprocessing/decomposition/agent_tasks/decompose_classification"

AVAILABLE_DC_TCONFIGS = {
    'v1': DC_SUITE_V1,
    'v2': DC_SUITE_V2,
    'v3': DC_SUITE_V3,
    'v4': DC_SUITE_V4
}


class AgentDecompClsTaskConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_DC_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v4',
               cache_table_name: str = "qp_decompcls_agent_task_cache",
               inferencestat_table_name: str = "qp_decompcls_agent_task_stat",
               verbose: bool = False, log_level: LogLevel = LogLevel.DISABLED) -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_DC_TCONFIGS[base_config_version],
            formate_context_func=dc_custom_formate, postprocess_answer_func=dc_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log_path=DC_LOG_PATH,
            verbose=verbose, log_level=log_level)
