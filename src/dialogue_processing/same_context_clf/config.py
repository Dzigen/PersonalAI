from typing import Dict

from .agent_tasks.same_context_clf import AgentSameCtxClsTaskConfigSelector
from ..utils import BaseAgentTaskConfigSelector

CTXCLS_MAIN_LOG_PATH = "log/dialogue_processing/same_context_clf/main"

CTX_CLS_AGENTASKS_SELECTORS_MAPPING: Dict[str, BaseAgentTaskConfigSelector] = {
    'same_ctx_clf': AgentSameCtxClsTaskConfigSelector
}