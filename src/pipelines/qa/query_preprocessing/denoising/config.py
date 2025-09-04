from .agent_tasks.stopwords_removing import AgentStopWordsRemovingTaskConfigSelector
from .agent_tasks.grammar_checking import AgentQueryGrammarCheckConfigSelector

QD_MAIN_LOG_PATH = "log/qa/query_preprocessing/denoising/main"

DEFAULT_SWREMV_TASK_CONFIG = AgentStopWordsRemovingTaskConfigSelector.select(base_config_version='v1')

DEFAULT_GRAMCHECK_TASK_CONFIG = AgentQueryGrammarCheckConfigSelector.select(base_config_version='v1')
