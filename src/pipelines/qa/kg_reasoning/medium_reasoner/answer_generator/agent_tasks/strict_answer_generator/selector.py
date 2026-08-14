from ........utils import AgentTaskSolverConfig, BaseAgentTaskConfigSelector
from ........utils.logger import LogLevel
from .general_parsers import sanswgen_custom_formate, sanswgen_custom_postprocess
from .v1 import SANSWGEN_SUITE_V1
from .v2 import SANSWGEN_SUITE_V2
from .v3 import SANSWGEN_SUITE_V3
from .v4 import SANSWGEN_SUITE_V4

SANSWGEN_LOG_PATH = "log/qa/kg_reasoner/medium/answer_generation/agent_tasks/strict_answer_generator"

AVAILABLE_SANSWGEN_TCONFIGS = {
    'v1': SANSWGEN_SUITE_V1,
    'v2': SANSWGEN_SUITE_V2,
    'v3': SANSWGEN_SUITE_V3,
    'v4': SANSWGEN_SUITE_V4
}


class AgentStrictAnswerGeneratorTaskConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_SANSWGEN_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v4',
               cache_table_name: str = "medreasn_sanswgen_agent_task_cache",
               inferencestat_table_name: str = "medreasn_sanswgen_agent_task_stat",
               verbose: bool = False, log_level: LogLevel = LogLevel.DISABLED) -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_SANSWGEN_TCONFIGS[base_config_version],
            formate_context_func=sanswgen_custom_formate, postprocess_answer_func=sanswgen_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log_path=SANSWGEN_LOG_PATH,
            verbose=verbose, log_level=log_level)
