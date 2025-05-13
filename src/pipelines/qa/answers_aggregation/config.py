from .agent_tasks.answers_summarisation import AgentSubASummTaskConfigSelector

AAGG_MAIN_LOG_PATH = "log/qa/answers_aggregation/main"

DEFAULT_ASUMM_TASK_CONFIG = AgentSubASummTaskConfigSelector.select(base_config_version='v1')