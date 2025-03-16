from .agent_tasks.judge import AgentLLMJudgeTaskConfigSelector

DEFAULT_LLMJUDGE_TASK_CONFIG = AgentLLMJudgeTaskConfigSelector.select(base_config_version='v1')
