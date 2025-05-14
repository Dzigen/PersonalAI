from .agent_tasks.answers_summarisation import AgentClueAnswersSummTaskConfigSelector

CQSUMM_MAIN_LOG_PATH =  "log/qa/kg_reasoner/medium/clueanswers_summarisation/main"
DEFAULT_CQSUMM_TASK_CONFIG = AgentClueAnswersSummTaskConfigSelector.select(base_config_version='v1') 
