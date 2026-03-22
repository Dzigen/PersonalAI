from typing import Dict

from .agent_tasks.thesis_extraction import AgentThesisExtrTaskConfigSelector
from .agent_tasks.triplet_extraction import AgentTripletExtrTaskConfigSelector
from ....utils import BaseAgentTaskConfigSelector

MEM_EXTRACTOR_MAIN_LOG_PATH = "log/memorize/extractor/main"

MEMEXTRACTOR_AGENTASKS_SELECTORS_MAPPING: Dict[str, BaseAgentTaskConfigSelector] = {
    'triplets_extraction': AgentTripletExtrTaskConfigSelector,
    'thesises_extraction': AgentThesisExtrTaskConfigSelector
}
