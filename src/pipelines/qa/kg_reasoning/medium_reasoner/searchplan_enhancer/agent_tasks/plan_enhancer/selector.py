from ........utils import AgentTaskSolverConfig, BaseAgentTaskConfigSelector
from ........utils.logger import LogLevel
from .general_parsers import planenh_custom_formate, planenh_custom_postprocess
from .v1 import PLANENH_SUITE_V1
from .v2 import PLANENH_SUITE_V2
from .v3 import PLANENH_SUITE_V3
from .v4 import PLANENH_SUITE_V4

PLANENH_LOG_PATH = "log/qa/kg_reasoner/medium/plan_enhancer/agent_tasks/plan_enhancing"

AVAILABLE_PLANENH_TCONFIGS = {
    'v1': PLANENH_SUITE_V1,
    'v2': PLANENH_SUITE_V2,
    'v3': PLANENH_SUITE_V3,
    'v4': PLANENH_SUITE_V4
}


class AgentPlanEnhancingTaskConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_PLANENH_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v4',
               cache_table_name: str = "medreasn_planenh_agent_task_cache",
               inferencestat_table_name: str = 'medreasn_planenh_agent_task_stat',
               verbose: bool = False, log_level: LogLevel = LogLevel.DISABLED) -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_PLANENH_TCONFIGS[base_config_version],
            formate_context_func=planenh_custom_formate, postprocess_answer_func=planenh_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log_path=PLANENH_LOG_PATH,
            verbose=verbose, log_level=log_level)
