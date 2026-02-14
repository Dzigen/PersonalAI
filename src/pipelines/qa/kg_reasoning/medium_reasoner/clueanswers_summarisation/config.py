from typing import Dict

from .agent_tasks.answers_summarisation import AgentClueAnswersSummTaskConfigSelector
from .....utils import BaseAgentTaskConfigSelector

CQSUMM_MAIN_LOG_PATH = "log/qa/kg_reasoner/medium/clueanswers_summarisation/main"


CQSUMM_AGENTASKS_SELECTORS_MAPPING: Dict[str, BaseAgentTaskConfigSelector] = {
    'canswers_summarisation': AgentClueAnswersSummTaskConfigSelector
}
