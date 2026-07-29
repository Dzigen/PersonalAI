from ........utils import AgentTaskSolverConfig, BaseAgentTaskConfigSelector
from ........utils.logger import LogLevel
from .general_parsers import enhcls_custom_formate, enhcls_custom_postprocess
from .v1 import ENHCLS_SUITE_V1
from .v2 import ENHCLS_SUITE_V2
from .v3 import ENHCLS_SUITE_V3
from .v4 import ENHCLS_SUITE_V4
from .v5 import ENHCLS_SUITE_V5

ENHCLS_LOG_PATH = "log/qa/kg_reasoner/medium/plan_enhancer/agent_tasks/enhance_classifier"

AVAILABLE_ENHCLS_TCONFIGS = {
    'v1': ENHCLS_SUITE_V1,
    'v2': ENHCLS_SUITE_V2,
    'v3': ENHCLS_SUITE_V3,
    'v4': ENHCLS_SUITE_V4,
    'v5': ENHCLS_SUITE_V5
}


class AgentEnhanceClassifierTaskConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_ENHCLS_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v5',
               cache_table_name: str = "medreasn_enhcls_agent_task_cache",
               inferencestat_table_name: str = "medreasn_enhcls_agent_task_stat",
               verbose: bool = False, log_level: LogLevel = LogLevel.DISABLED) -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_ENHCLS_TCONFIGS[base_config_version],
            formate_context_func=enhcls_custom_formate, postprocess_answer_func=enhcls_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log_path=ENHCLS_LOG_PATH,
            verbose=verbose, log_level=log_level)
