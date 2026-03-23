from typing import Dict

from .agent_tasks.clueanswer_generation import AgentClueAnswerGenTaskConfigSelector
from ......utils import BaseAgentTaskConfigSelector

CAGEN_MAIN_LOG_PATH = "log/qa/kg_reasoner/medium/clueansw_generation/main"

CAGEN_AGENTASKS_SELECTORS_MAPPING: Dict[str, BaseAgentTaskConfigSelector] = {
    'cagen': AgentClueAnswerGenTaskConfigSelector
}
