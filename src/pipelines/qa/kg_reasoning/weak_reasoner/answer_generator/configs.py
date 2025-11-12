from typing import Dict

from .agent_tasks.ag import AgentSimpleAGTaskConfigSelector
from .....utils import BaseAgentTaskConfigSelector

AG_MAIN_LOG_PATH = 'log/qa/kg_reasoner/weak/answer_generation/main'

ANSWGEN_AGENTASKS_SELECTORS_MAPPING: Dict[str, BaseAgentTaskConfigSelector] = {
    'ag': AgentSimpleAGTaskConfigSelector
}