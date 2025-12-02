from ........utils import AgentTaskSolverConfig, Logger
from .......utils import BaseAgentTaskConfigSelector
from .general_parsers import planenh_custom_formate, planenh_custom_postprocess
from .v1 import PLANENH_SUITE_V1
from .v2 import PLANENH_SUITE_V2

PLANENH_LOG_PATH = "log/qa/kg_reasoner/medium/plan_enhancer/agent_tasks/plan_enhancing"

AVAILABLE_PLANENH_TCONFIGS = {
    'v1': PLANENH_SUITE_V1,
    'v2': PLANENH_SUITE_V2
}


class AgentPlanEnhancingTaskConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_PLANENH_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v2',
               cache_table_name: str = "medreasn_planenh_agent_task_cache",
               inferencestat_table_name: str = 'medreasn_planenh_agent_task_stat') -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_PLANENH_TCONFIGS[base_config_version],
            formate_context_func=planenh_custom_formate, postprocess_answer_func=planenh_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log=Logger(PLANENH_LOG_PATH))
