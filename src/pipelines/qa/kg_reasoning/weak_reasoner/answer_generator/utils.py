from dataclasses import dataclass, field
from typing import Dict, Union

from .configs import ANSWGEN_AGENTASKS_SELECTORS_MAPPING
from .....utils import BaseTaskSolvers, BaseAgentTaskConfigSelector, BaseAgentTasksConfig
from ......utils import AgentTaskSolver, AgentTaskSolverConfig

@dataclass
class WeakAGeneratorTaskSolvers(BaseTaskSolvers):
    answer_generator_solver: AgentTaskSolver

@dataclass
class QALLMGeneratorAgentTasksConfig(BaseAgentTasksConfig):
    """
    :param ag: Конфигурация атомарной задачи для LLM-агента по условной генерации ответа на вопрос. Значение по умолчанию 'v3'.
    :type ag: AgentTaskSolverConfig, optional
    """
    ag: Union[AgentTaskSolverConfig, str] = 'v3'

    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector] = field(default_factory=lambda: ANSWGEN_AGENTASKS_SELECTORS_MAPPING)