from .agent_tasks.query_decomposition import AgentQueryDecompTaskConfigSelector


QD_MAIN_LOG_PATH = "log/qa/query_preprocessing/decomposition/main"

DEFAULT_QD_TASK_CONFIG = AgentQueryDecompTaskConfigSelector.select(base_config_version='v1')