from typing import Dict

from .agent_tasks.kw_extraction import AgentKWETaskConfigSelector
from ......utils import BaseAgentTaskConfigSelector

QP_MAIN_LOG_PATH = 'log/qa/kg_reasoner/weak/query_parser/main'

KWEXTR_AGENTASKS_SELECTORS_MAPPING: Dict[str, BaseAgentTaskConfigSelector] = {
    'kw_extraction': AgentKWETaskConfigSelector
}
