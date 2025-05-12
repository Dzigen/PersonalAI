from .agent_tasks.ag import AgentAGTaskConfigSelector

AG_MAIN_LOG_PATH = 'log/qa/kg_reasoner/weak/answer_generation/main'
DEFAULT_AG_TASK_CONFIG =  AgentAGTaskConfigSelector.select(base_config_version='v2')
