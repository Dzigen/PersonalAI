from dataclasses import dataclass, field
from typing import Dict, Union
from copy import deepcopy

from .config import ASSIST_USE_CLS_AGENTASKS_SELECTORS_MAPPING
from ..utils import BaseTaskSolvers, BaseAgentTasksConfig, BaseAgentTaskConfigSelector
from ...utils.task_solver import AgentTaskSolver, AgentTaskSolverConfig


@dataclass
class AssistUseClsTaskSolvers(BaseTaskSolvers):
    """Контейнер атомарных LLM-задач для разбиения пользовательских сообщений на группы.

    :param same_ctx_solver: Задача классификации сообщения пользователя на предмет соответствия контексту предыдущего сообщения.
    :type same_ctx_solver: AgentTaskSolver
    """
    assist_use_solver: AgentTaskSolver


@dataclass
class AssistUseClsAgentTasksConfig(BaseAgentTasksConfig):
    """
    :param same_ctx_clf: Конфигурация атомарной задачи для LLM-агента по классификации сообщения. Значение по умолчанию 'v1'.
    :type same_ctx_clf: Union[AgentTaskSolverConfig, str], optional
    """
    assist_use_clf: Union[AgentTaskSolverConfig, str] = 'v1'

    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector] = field(default_factory=lambda: ASSIST_USE_CLS_AGENTASKS_SELECTORS_MAPPING)

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = AssistUseClsAgentTasksConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config
