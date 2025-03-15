from .agent_tasks.judge import AgentLLMJudgeTaskConfigSelector

EVAL_JUDGE_MAIN_LOG_PATH = 'log/eval/judge'
DEFAULT_LLMJUDGE_TASK_CONFIG =  AgentLLMJudgeTaskConfigSelector.select(base_config_version='v1')
