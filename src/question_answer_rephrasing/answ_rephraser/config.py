from typing import Dict

from .agent_tasks.answ_rephraser import AgentAnswRephTaskConfigSelector
from ...dialogue_processing.utils import BaseAgentTaskConfigSelector


ANSWRPH_MAIN_LOG_PATH = "log/question_answer_rephrasing/answer_processing/answ_rephraser/main"

ANSW_REPH_AGENTASKS_SELECTORS_MAPPING: Dict[str, BaseAgentTaskConfigSelector] = {
    'answer_rephraser': AgentAnswRephTaskConfigSelector,
}