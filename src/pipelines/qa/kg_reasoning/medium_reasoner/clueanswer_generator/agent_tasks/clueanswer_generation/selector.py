from ........utils import AgentTaskSolverConfig, BaseAgentTaskConfigSelector
from ........utils.logger import LogLevel
from .general_parsers import cagen_custom_formate, cagen_custom_postprocess
from .v1 import CAGEN_SUITE_V1
from .v2 import CAGEN_SUITE_V2
from .v3 import CAGEN_SUITE_V3
from .v4 import CAGEN_SUITE_V4
from .v5 import CAGEN_SUITE_V5

CAGEN_LOG_PATH = "log/qa/kg_reasoner/medium/clueansw_generation/agent_tasks/canswer_generator"

AVAILABLE_CAGEN_TCONFIGS = {
    'v1': CAGEN_SUITE_V1,
    'v2': CAGEN_SUITE_V2,
    'v3': CAGEN_SUITE_V3,
    'v4': CAGEN_SUITE_V4,
    'v5': CAGEN_SUITE_V5
}


class AgentClueAnswerGenTaskConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_CAGEN_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v5',
               cache_table_name: str = "medreasn_cagen_agent_task_cache",
               inferencestat_table_name: str = "medreasn_cagen_agent_task_stat",
               verbose: bool = False, log_level: LogLevel = LogLevel.DISABLED) -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_CAGEN_TCONFIGS[base_config_version],
            formate_context_func=cagen_custom_formate, postprocess_answer_func=cagen_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log_path=CAGEN_LOG_PATH,
            verbose=verbose, log_level=log_level)
