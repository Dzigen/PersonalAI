from ........utils import AgentTaskSolverConfig, BaseAgentTaskConfigSelector
from ........utils.logger import LogLevel
from .general_parsers import planinit_custom_formate, planinit_custom_postprocess
from .v1 import PLANINIT_SUITE_V1
from .v2 import PLANINIT_SUITE_V2

PLANINIT_LOG_PATH = "log/qa/kg_reasoner/medium/plan_enhancer/agent_tasks/plan_initialisation"

AVAILABLE_PLANINIT_TCONFIGS = {
    'v1': PLANINIT_SUITE_V1,
    'v2': PLANINIT_SUITE_V2
}


class AgentPlanInitTaskConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_PLANINIT_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v2',
               cache_table_name: str = "medreasn_planinit_agent_task_cache",
               inferencestat_table_name: str = "medreasn_planinit_agent_task_stat",
               verbose: bool = False, log_level: LogLevel = LogLevel.DISABLED) -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_PLANINIT_TCONFIGS[base_config_version],
            formate_context_func=planinit_custom_formate, postprocess_answer_func=planinit_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log_path=PLANINIT_LOG_PATH,
            verbose=verbose, log_level=log_level)
