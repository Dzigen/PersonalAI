from ........utils import AgentTaskSolverConfig, Logger
from .......utils import BaseAgentTaskConfigSelector
from .general_parsers import cagen_custom_formate, cagen_custom_postprocess
from .v1 import CAGEN_SUITE_V1
from .v2 import CAGEN_SUITE_V2
from .v3 import CAGEN_SUITE_V3

CAGEN_LOG_PATH = "log/qa/kg_reasoner/medium/clueansw_generation/agent_tasks/canswer_generator"

AVAILABLE_CAGEN_TCONFIGS = {
    'v1': CAGEN_SUITE_V1,
    'v2': CAGEN_SUITE_V2,
    'v3': CAGEN_SUITE_V3
}


class AgentClueAnswerGenTaskConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_CAGEN_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v3',
               cache_table_name: str = "medreasn_cagen_agent_task_cache",
               inferencestat_table_name: str = "medreasn_cagen_agent_task_stat") -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_CAGEN_TCONFIGS[base_config_version],
            formate_context_func=cagen_custom_formate, postprocess_answer_func=cagen_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log=Logger(CAGEN_LOG_PATH))
