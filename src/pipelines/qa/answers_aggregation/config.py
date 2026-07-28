from typing import Dict

from .agent_tasks.strict_answers_summarisation import AgentStrictSubASummTaskConfigSelector
from .agent_tasks.casual_answers_summarisation import AgentCasualSubASummTaskConfigSelector
from ....utils import BaseAgentTaskConfigSelector

AAGG_MAIN_LOG_PATH = "log/qa/answers_aggregation/main"

ANSWAGGR_AGENTASKS_SELECTORS_MAPPING: Dict[str, BaseAgentTaskConfigSelector] = {
    'strict_suba_summarisation': AgentStrictSubASummTaskConfigSelector,
    'casual_suba_summarisation': AgentCasualSubASummTaskConfigSelector
}
