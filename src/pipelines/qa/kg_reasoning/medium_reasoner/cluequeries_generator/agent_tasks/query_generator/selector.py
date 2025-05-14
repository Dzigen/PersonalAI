from ........utils import AgentTaskSolverConfig, Logger
from .general_parsers import qgen_custom_formate, qgen_custom_postprocess
from .v1 import QGEN_SUITE_V1

QGEN_LOG_PATH = "log/qa/kg_reasoner/medium/cluequeries_generator/agent_tasks/query_generator"

AVAILABLE_QGEN_TCONFIGS = {
    'v1': QGEN_SUITE_V1
}

class AgentQueryGenTaskConfigSelector:
    @staticmethod
    def get_available_configs():
        return AVAILABLE_QGEN_TCONFIGS

    @staticmethod
    def select(base_config_version:str = 'v1', cache_table_name:str="medreasn_qgen_agent_task_cache") -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_QGEN_TCONFIGS[base_config_version],
            formate_context_func=qgen_custom_formate, postprocess_answer_func=qgen_custom_postprocess,
            cache_table_name=cache_table_name,
            log=Logger(QGEN_LOG_PATH))