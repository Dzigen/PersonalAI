from dataclasses import dataclass, field
from typing import Dict, Union
from copy import deepcopy

from .config import FCT_PRSRV_AGENTASKS_SELECTORS_MAPPING
from ..utils import BaseTaskSolvers, BaseAgentTasksConfig, BaseAgentTaskConfigSelector
from ...utils.task_solver import AgentTaskSolver, AgentTaskSolverConfig


@dataclass
class FactPreserverTaskSolvers(BaseTaskSolvers):
    """Контейнер атомарных LLM-задач для суммаризации сообщений.

    :param fact_preserving_solver: Задача суммаризации сообщений, длина которых превосходит допустимое значение.
    :type fact_preserving_solver: AgentTaskSolver
    """
    fact_preserving_solver: AgentTaskSolver
    reject_answer_cls_solver: AgentTaskSolver


@dataclass
class FactPreserverAgentTasksConfig(BaseAgentTasksConfig):
    """
    :param msg_summarisation: Конфигурация атомарной задачи для LLM-агента по суммаризации сообщения. Значение по умолчанию 'v1'.
    :type msg_summarisation: Union[AgentTaskSolverConfig, str], optional
    """
    msg_summarisation: Union[AgentTaskSolverConfig, str] = 'v1'
    reject_answer_cls: Union[AgentTaskSolverConfig, str] = 'v1'

    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector] = field(default_factory=lambda: FCT_PRSRV_AGENTASKS_SELECTORS_MAPPING)

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = FactPreserverAgentTasksConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config
