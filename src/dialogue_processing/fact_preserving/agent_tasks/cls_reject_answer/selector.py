from ....utils import AgentTaskSolverConfig
from src.utils import Logger
from src.dialogue_processing.utils import BaseAgentTaskConfigSelector
from .general_parsers import reject_answ_cls_custom_formate, reject_answ_cls_custom_postprocess
from .v1 import REJECT_ANSW_CLS_SUITE_V1
from .v2 import REJECT_ANSW_CLS_SUITE_V2

REJECT_ANSW_CLS_LOG_PATH = "log/dialogue_processing/fact_preserving/agent_tasks/cls_reject_answer"

AVAILABLE_REJECT_ANSW_CLS_TCONFIGS = {
    'v1': REJECT_ANSW_CLS_SUITE_V1,
    'v2': REJECT_ANSW_CLS_SUITE_V2
}

class AgentRejectAnswClsTaskConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_REJECT_ANSW_CLS_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v1',
               cache_table_name: str = "reject_answ_cls_agent_task_cache",
               inferencestat_table_name: str = "reject_answ_cls_agent_task_stat") -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_REJECT_ANSW_CLS_TCONFIGS[base_config_version],
            formate_context_func=reject_answ_cls_custom_formate, postprocess_answer_func=reject_answ_cls_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log=Logger(REJECT_ANSW_CLS_LOG_PATH))
