from typing import Dict

from .agent_tasks.entities_extractor import AgentEntitiesExtrTaskConfigSelector
from .....utils import BaseAgentTaskConfigSelector

ENEXTR_MAIN_LOG_PATH = "log/qa/kg_reasoner/medium/entities_extractor/main"


ENTEXTR_AGENTASKS_SELECTORS_MAPPING: Dict[str, BaseAgentTaskConfigSelector] = {
    'entities_extraction': AgentEntitiesExtrTaskConfigSelector
}