from typing import Dict

from .agent_tasks.answers_summarisation import AgentSubASummTaskConfigSelector
from ....utils import BaseAgentTaskConfigSelector

AAGG_MAIN_LOG_PATH = "log/qa/answers_aggregation/main"

ANSWAGGR_AGENTASKS_SELECTORS_MAPPING: Dict[str, BaseAgentTaskConfigSelector] = {
    'suba_summarisation': AgentSubASummTaskConfigSelector
}
