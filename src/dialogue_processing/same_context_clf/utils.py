from dataclasses import dataclass, field
from typing import Dict, Union
from copy import deepcopy

from .config import CTX_CLS_AGENTASKS_SELECTORS_MAPPING
from ..utils import BaseTaskSolvers, BaseAgentTasksConfig, BaseAgentTaskConfigSelector
from ...utils.task_solver import AgentTaskSolver, AgentTaskSolverConfig


@dataclass
class SameCtxClsTaskSolvers(BaseTaskSolvers):
    """Контейнер атомарных LLM-задач для разбиения пользовательских сообщений на группы.

    :param same_ctx_solver: Задача классификации сообщения пользователя на предмет соответствия контексту предыдущего сообщения.
    :type same_ctx_solver: AgentTaskSolver
    """
    same_ctx_solver: AgentTaskSolver


@dataclass
class SameCtxClsAgentTasksConfig(BaseAgentTasksConfig):
    """
    :param same_ctx_clf: Конфигурация атомарной задачи для LLM-агента по классификации сообщения. Значение по умолчанию 'v1'.
    :type same_ctx_clf: Union[AgentTaskSolverConfig, str], optional
    """
    same_ctx_clf: Union[AgentTaskSolverConfig, str] = 'v1'

    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector] = field(default_factory=lambda: CTX_CLS_AGENTASKS_SELECTORS_MAPPING)

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = SameCtxClsAgentTasksConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config
