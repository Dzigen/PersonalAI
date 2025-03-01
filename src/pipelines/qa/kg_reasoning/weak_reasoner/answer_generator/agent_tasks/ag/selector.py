from ........utils import AgentTaskSolverConfig, Logger
from ........db_drivers.kv_driver import KeyValueDriverConfig
from .general_parsers import ag_custom_formate, ag_custom_postprocess
from .v2 import ANSWER_GEN_SUITE_V2
from .v1 import ANSWER_GEN_SUITE_V1

ANSWER_GENERATION_LOG_PATH = 'log/qa/kg_reasoner/weak/answer_generation/agent_tasks/ag'

AVAILABLE_AG_TCONFIGS = {
    'v1': ANSWER_GEN_SUITE_V1,
    'v2': ANSWER_GEN_SUITE_V2
}

class AgentAGTaskConfigSelector:
    @staticmethod
    def get_available_configs():
        return AVAILABLE_AG_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v1', kvcache_driver_config: KeyValueDriverConfig = None) -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            suites=AVAILABLE_AG_TCONFIGS[base_config_version],
            formate_context_func=ag_custom_formate, postprocess_answer_func=ag_custom_postprocess,
            cache_kvdriver_config=kvcache_driver_config,
            log=Logger(ANSWER_GENERATION_LOG_PATH))
