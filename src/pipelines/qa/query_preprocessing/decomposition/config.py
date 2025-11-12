from typing import Dict
from .agent_tasks.query_decomposition import AgentQueryDecompTaskConfigSelector
from .agent_tasks.decomposition_classifier import AgentDecompClsTaskConfigSelector
from ....utils import BaseAgentTaskConfigSelector

QD_MAIN_LOG_PATH = "log/qa/query_preprocessing/decomposition/main"

QUERYDECOMP_AGENTASKS_SELECTORS_MAPPING: Dict[str, BaseAgentTaskConfigSelector] = {
    'classify': AgentDecompClsTaskConfigSelector,
    'decompose': AgentQueryDecompTaskConfigSelector
}