from typing import Dict

from .agent_tasks.chunk_rephraser import AgentRephChunkTaskConfigSelector
from ..utils import BaseAgentTaskConfigSelector

from ..fact_preserving.agent_tasks.cls_reject_answer import AgentRejectAnswClsTaskConfigSelector

RPHCHNK_MAIN_LOG_PATH = "log/dialogue_processing/chunk_rephraser/main"

REPH_CHNK_AGENTASKS_SELECTORS_MAPPING: Dict[str, BaseAgentTaskConfigSelector] = {
    'reph_chunk': AgentRephChunkTaskConfigSelector,
    'reject_answer_cls': AgentRejectAnswClsTaskConfigSelector
}