from dataclasses import dataclass, field
from typing import Dict, Union
from copy import deepcopy

from .config import REPH_CHNK_AGENTASKS_SELECTORS_MAPPING
from ..utils import BaseTaskSolvers, BaseAgentTasksConfig, BaseAgentTaskConfigSelector
from ...utils.task_solver import AgentTaskSolver, AgentTaskSolverConfig


@dataclass
class RephChunkTaskSolvers(BaseTaskSolvers):
    """Контейнер атомарных LLM-задач для переформулирования сообщений.

    :param same_ctx_solver: Задача переформулирования сообщений.
    :type same_ctx_solver: AgentTaskSolver
    """
    reph_chunk_solver: AgentTaskSolver
    reject_answer_cls_solver: AgentTaskSolver


@dataclass
class RephChunkAgentTasksConfig(BaseAgentTasksConfig):
    """
    :param reph_chunk: Конфигурация атомарной задачи для LLM-агента по переформулированию сообщений в чанке. Значение по умолчанию 'v1'.
    :type reph_chunk: Union[AgentTaskSolverConfig, str], optional
    """
    reph_chunk: Union[AgentTaskSolverConfig, str] = 'v1'
    reject_answer_cls: Union[AgentTaskSolverConfig, str] = 'v1'

    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector] = field(default_factory=lambda: REPH_CHNK_AGENTASKS_SELECTORS_MAPPING)

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = RephChunkAgentTasksConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config
