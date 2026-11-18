from typing import Dict

from .agent_tasks.judge import AgentLLMJudgeTaskConfigSelector
from ..utils.task_solver import BaseAgentTaskConfigSelector


EVAL_JUDGE_MAIN_LOG_PATH = 'log/eval/judge'

JUDGE_AGENTASKS_SELECTORS_MAPPING: Dict[str, BaseAgentTaskConfigSelector] = {
    'llmasajudge': AgentLLMJudgeTaskConfigSelector
}