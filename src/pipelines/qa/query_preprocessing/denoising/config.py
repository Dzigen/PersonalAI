from typing import Dict

from .agent_tasks.stopwords_removing import AgentStopWordsRemovingTaskConfigSelector
from .agent_tasks.grammar_checking import AgentQueryGrammarCheckConfigSelector
from ....utils import BaseAgentTaskConfigSelector

QD_MAIN_LOG_PATH = "log/qa/query_preprocessing/denoising/main"

QUERYDENOIS_AGENTASKS_SELECTORS_MAPPING: Dict[str, BaseAgentTaskConfigSelector] = {
    'swremoval': AgentStopWordsRemovingTaskConfigSelector,
    'grammarcheck': AgentQueryGrammarCheckConfigSelector
}
    
