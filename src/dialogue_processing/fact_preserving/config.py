from typing import Dict

from .agent_tasks.fact_preserving import AgentFactPreservTaskConfigSelector
from .agent_tasks.cls_reject_answer import AgentRejectAnswClsTaskConfigSelector
from ..utils import BaseAgentTaskConfigSelector

FACT_PRESERVE_MAIN_LOG_PATH = "log/dialogue_processing/fact_preserving/main"


FCT_PRSRV_AGENTASKS_SELECTORS_MAPPING: Dict[str, BaseAgentTaskConfigSelector] = {
    'msg_summarisation': AgentFactPreservTaskConfigSelector,
    'reject_answer_cls': AgentRejectAnswClsTaskConfigSelector
}