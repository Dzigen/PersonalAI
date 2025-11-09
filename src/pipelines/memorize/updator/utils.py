from dataclasses import dataclass, field
from typing import Dict, Union
from copy import deepcopy

from .config import MEMUPDATOR_AGENTASKS_SELECTORS_MAPPING
from ...utils import BaseTaskSolvers, BaseAgentTasksConfig, BaseAgentTaskConfigSelector
from ....utils import AgentTaskSolver, AgentTaskSolverConfig


@dataclass
class MemUpdatorTaskSolvers(BaseTaskSolvers):
    replace_simple_solver: AgentTaskSolver
    replace_hyper_solver: AgentTaskSolver


@dataclass
class MemUpdatorAgentTasksConfig(BaseAgentTasksConfig):
    """
    :param replace_simple_task_config: Конфигурация атомарной задачи для LLM-агента по поиску устаревших триплетов типа "simple". Значение по умолчанию 'v1'.
    :type replace_simple_task_config: AgentTaskSolverConfig, optional
    :param replace_thesis_task_config: Конфигурация атомарной задачи для LLM-агента по поиску устаревших триплетов типа "hyper". Значение по умолчанию 'v1'.
    :type replace_thesis_task_config: AgentTaskSolverConfig, optional
    """
    replace_simple: Union[AgentTaskSolverConfig, str] = 'v1'
    replace_thesis: Union[AgentTaskSolverConfig, str] = 'v1'

    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector] = field(default_factory=lambda: MEMUPDATOR_AGENTASKS_SELECTORS_MAPPING)

    @staticmethod
    def from_dict(dict_config):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = MemUpdatorAgentTasksConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config
