from typing import Dict

from .agent_tasks.answer_generator import AgentAnswerGeneratorTaskConfigSelector
from .agent_tasks.answer_trying_classifier import AgentAnswerClassifierTaskConfigSelector
from .....utils import BaseAgentTaskConfigSelector

ANSWGEN_MAIN_LOG_PATH = "log/qa/kg_reasoner/medium/answer_generation/main"


ANSWGEN_AGENTASKS_SELECTORS_MAPPING: Dict[str, BaseAgentTaskConfigSelector] = {
    'answer_classifier': AgentAnswerClassifierTaskConfigSelector,
    'answer_generator': AgentAnswerGeneratorTaskConfigSelector
}