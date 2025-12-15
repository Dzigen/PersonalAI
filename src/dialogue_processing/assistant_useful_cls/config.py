from typing import Dict

from .agent_tasks.assistant_useful_cls import AgentAssistUsefulClsTaskConfigSelector
from ..utils import BaseAgentTaskConfigSelector

ASUCLS_MAIN_LOG_PATH = "log/dialogue_processing/assistant_useful_cls/main"

ASSIST_USE_CLS_AGENTASKS_SELECTORS_MAPPING: Dict[str, BaseAgentTaskConfigSelector] = {
    'assist_use_clf': AgentAssistUsefulClsTaskConfigSelector
}