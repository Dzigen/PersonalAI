from dataclasses import dataclass, field
from typing import Dict, Union
from copy import deepcopy

from .config import QUEST_REPH_AGENTASKS_SELECTORS_MAPPING
from ...dialogue_processing.utils import BaseTaskSolvers, BaseAgentTasksConfig, BaseAgentTaskConfigSelector
from ...utils.task_solver import AgentTaskSolver, AgentTaskSolverConfig


@dataclass
class QuestRephTaskSolvers(BaseTaskSolvers):
    """Контейнер атомарных LLM-задач для переформулирования вопросов.

    :param quest_rephraser_solver: Задача переформулирования вопросов.
    :type quest_rephraser_solver: AgentTaskSolver
    """
    quest_rephraser_solver: AgentTaskSolver
    reject_answer_cls_solver: AgentTaskSolver


@dataclass
class QuestRephAgentTasksConfig(BaseAgentTasksConfig):
    """
    :param quest_rephraser: Конфигурация атомарной задачи для LLM-агента по переформулированию вопросов. Значение по умолчанию 'v1'.
    :type quest_rephraser: Union[AgentTaskSolverConfig, str], optional
    """
    quest_rephraser: Union[AgentTaskSolverConfig, str] = 'v1'
    reject_answer_cls: Union[AgentTaskSolverConfig, str] = 'v2'

    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector] = field(default_factory=lambda: QUEST_REPH_AGENTASKS_SELECTORS_MAPPING)

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = QuestRephAgentTasksConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config
