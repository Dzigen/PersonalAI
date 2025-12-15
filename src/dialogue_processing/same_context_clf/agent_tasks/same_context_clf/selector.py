from ....utils import AgentTaskSolverConfig
from src.utils import Logger
from src.dialogue_processing.utils import BaseAgentTaskConfigSelector
from .general_parsers import same_ctx_cls_custom_formate, same_ctx_cls_custom_postprocess
from .v1 import SAME_CTX_CLS_SUITE_V1

SAME_CTX_CLS_LOG_PATH = "log/dialogue_processing/same_context_clf/agent_tasks/same_context_clf"

AVAILABLE_SAME_CTX_CLS_TCONFIGS = {
    'v1': SAME_CTX_CLS_SUITE_V1,
}


class AgentSameCtxClsTaskConfigSelector(BaseAgentTaskConfigSelector):
    @staticmethod
    def get_available_configs():
        return AVAILABLE_SAME_CTX_CLS_TCONFIGS

    @staticmethod
    def select(base_config_version: str = 'v1',
               cache_table_name: str = "same_ctx_cls_agent_task_cache",
               inferencestat_table_name: str = "same_ctx_cls_agent_task_stat") -> AgentTaskSolverConfig:
        return AgentTaskSolverConfig(
            version=base_config_version,
            suites=AVAILABLE_SAME_CTX_CLS_TCONFIGS[base_config_version],
            formate_context_func=same_ctx_cls_custom_formate, postprocess_answer_func=same_ctx_cls_custom_postprocess,
            cache_table_name=cache_table_name,
            inferencestat_table_name=inferencestat_table_name,
            log=Logger(SAME_CTX_CLS_LOG_PATH))
