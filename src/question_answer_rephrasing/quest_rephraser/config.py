from typing import Dict

from .agent_tasks.quest_rephraser import AgentQuestRephTaskConfigSelector
from src.dialogue_processing.fact_preserving.agent_tasks.cls_reject_answer import AgentRejectAnswClsTaskConfigSelector
from ...dialogue_processing.utils import BaseAgentTaskConfigSelector


QSTRPH_MAIN_LOG_PATH = "log/question_answer_rephrasing/question_processing/quest_rephraser/main"

QUEST_REPH_AGENTASKS_SELECTORS_MAPPING: Dict[str, BaseAgentTaskConfigSelector] = {
    'quest_rephraser': AgentQuestRephTaskConfigSelector,
    'reject_answer_cls': AgentRejectAnswClsTaskConfigSelector
}