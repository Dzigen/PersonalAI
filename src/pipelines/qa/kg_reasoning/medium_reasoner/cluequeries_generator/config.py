from .agent_tasks.query_generator import AgentQueryGenTaskConfigSelector

CQGEN_MAIN_LOG_PATH = "log/qa/kg_reasoner/medium/cluequeries_generator/main" 
DEFAULT_CQGEN_TASK_CONFIG = AgentQueryGenTaskConfigSelector.select(base_config_version='v1')
