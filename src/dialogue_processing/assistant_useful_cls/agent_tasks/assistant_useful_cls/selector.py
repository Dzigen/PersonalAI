from ....utils import AgentTaskSolverConfig
from src.utils import Logger
from src.dialogue_processing.utils import BaseAgentTaskConfigSelector
from .general_parsers import assist_use_cls_custom_formate, assist_use_cls_custom_postprocess
from .v1 import ASSIST_USE_CLS_SUITE_V1

ASSIST_USE_CLS_LOG_PATH = "log/dialogue_processing/assistant_useful_cls/agent_tasks/assistant_useful_cls"

AVAILABLE_ASSIST_USE_CLS_TCONFIGS = {
    'v1': ASSIST_USE_CLS_SUITE_V1,
}

class AgentAssistUsefulClsTaskConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_ASSIST_USE_CLS_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v1',
               cache_table_name: str = "assist_use_cls_agent_task_cache",
               inferencestat_table_name: str = "assist_use_cls_agent_task_stat") -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_ASSIST_USE_CLS_TCONFIGS[base_config_version],
            formate_context_func=assist_use_cls_custom_formate, postprocess_answer_func=assist_use_cls_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log=Logger(ASSIST_USE_CLS_LOG_PATH))
