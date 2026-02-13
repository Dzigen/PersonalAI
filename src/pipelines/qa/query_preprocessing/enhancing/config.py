from typing import Dict

from .agent_tasks.query_expanstion import AgentQueryExpansionCheckConfigSelector
from .agent_tasks.terms_check import AgentQueryTermsCheckConfigSelector
from .agent_tasks.linguist_check import AgentQueryLinguistCheckConfigSelector
from ....utils import BaseAgentTaskConfigSelector

QE_MAIN_LOG_PATH = "log/qa/query_preprocessing/enhancing/main"

QUERYENH_AGENTASKS_SELECTORS_MAPPING: Dict[str, BaseAgentTaskConfigSelector] = {
    'qexpan': AgentQueryExpansionCheckConfigSelector,
    'termscheck': AgentQueryTermsCheckConfigSelector,
    'lingcheck': AgentQueryLinguistCheckConfigSelector
}
