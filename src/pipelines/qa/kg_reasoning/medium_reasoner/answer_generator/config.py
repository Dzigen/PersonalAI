from typing import Dict

from .agent_tasks.casual_answer_generator import AgentCasualAnswerGeneratorTaskConfigSelector
from .agent_tasks.strict_answer_generator import AgentStrictAnswerGeneratorTaskConfigSelector
from .agent_tasks.answer_trying_classifier import AgentAnswerClassifierTaskConfigSelector
from ......utils import BaseAgentTaskConfigSelector

ANSWGEN_MAIN_LOG_PATH = "log/qa/kg_reasoner/medium/answer_generation/main"


ANSWGEN_AGENTASKS_SELECTORS_MAPPING: Dict[str, BaseAgentTaskConfigSelector] = {
    'answer_classifier': AgentAnswerClassifierTaskConfigSelector,
    'strict_answer_generator': AgentStrictAnswerGeneratorTaskConfigSelector,
    'casual_answer_generator': AgentCasualAnswerGeneratorTaskConfigSelector
}
