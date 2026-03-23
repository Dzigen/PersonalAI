from typing import Dict

from .agent_tasks.replace_simple_triplets import AgentReplSimpleTripletTaskConfigSelector
from .agent_tasks.replace_thesis_triplets import AgentReplThesisTripletTaskConfigSelector
from ....utils import BaseAgentTaskConfigSelector

MEM_UPDATOR_MAIN_LOG_PATH = "log/memorize/updator/main"

MEMUPDATOR_AGENTASKS_SELECTORS_MAPPING: Dict[str, BaseAgentTaskConfigSelector] = {
    'replace_simple': AgentReplSimpleTripletTaskConfigSelector,
    'replace_thesis': AgentReplThesisTripletTaskConfigSelector
}
