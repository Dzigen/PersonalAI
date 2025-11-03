from dataclasses import dataclass, field
from typing import Union, Dict

from .configs import KWEXTR_AGENTASKS_SELECTORS_MAPPING
from .....utils import BaseTaskSolvers, BaseAgentTaskConfigSelector, BaseAgentTasksConfig
from ......utils import AgentTaskSolver, AgentTaskSolverConfig

@dataclass
class WeakQueryParserTaskSolvers(BaseTaskSolvers):
    kw_extraction_solver: AgentTaskSolver

@dataclass
class QueryLLMParserAgentTasksConfig(BaseAgentTasksConfig):
    """
    :param kw_extraction: Конфигурация атомарной задачи для LLM-агента по извлечению ключевых сущностей из текста. Значение по умолчанию 'v2'.
    :type kw_extraction: AgentTaskSolverConfig, optional
    """
    kw_extraction: Union[AgentTaskSolverConfig, str] = 'v2'

    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector] = field(default_factory=lambda: KWEXTR_AGENTASKS_SELECTORS_MAPPING)