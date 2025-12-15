from dataclasses import dataclass, field
from typing import Dict, Union
from copy import deepcopy

from .config import ANSW_REPH_AGENTASKS_SELECTORS_MAPPING
from ...dialogue_processing.utils import BaseTaskSolvers, BaseAgentTasksConfig, BaseAgentTaskConfigSelector
from ...utils.task_solver import AgentTaskSolver, AgentTaskSolverConfig


@dataclass
class AnswRephTaskSolvers(BaseTaskSolvers):
    """Контейнер атомарных LLM-задач для переформулирования ответа.

    :param answ_rephraser_solver: Задача переформулирования вопросов.
    :type answ_rephraser_solver: AgentTaskSolver
    """
    answer_rephraser_solver: AgentTaskSolver


@dataclass
class AnswRephAgentTasksConfig(BaseAgentTasksConfig):
    """
    :param quest_rephraser: Конфигурация атомарной задачи для LLM-агента по переформулированию вопросов. Значение по умолчанию 'v1'.
    :type quest_rephraser: Union[AgentTaskSolverConfig, str], optional
    """
    answer_rephraser: Union[AgentTaskSolverConfig, str] = 'v1'

    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector] = field(default_factory=lambda: ANSW_REPH_AGENTASKS_SELECTORS_MAPPING)

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = AnswRephAgentTasksConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config
