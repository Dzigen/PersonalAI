from dataclasses import dataclass, field
from typing import Dict, Union
from copy import deepcopy
from enum import Enum

from .config import ANSWAGGR_AGENTASKS_SELECTORS_MAPPING
from ...utils import BaseTaskSolvers
from ....utils.task_solver import AgentTaskSolver, AgentTaskSolverConfig, BaseAgentTasksConfig, BaseAgentTaskConfigSelector


@dataclass
class AnswerAggregatorTaskSolvers(BaseTaskSolvers):
    """Контейнер атомарных LLM-задач для агрегации ответов.

    :param strict_subanswers_summarisation_solver: Задача суммаризации/объединения независимых ответов на под-вопросы в один финальный ответ (c возможностью генерации <|NotEnoughtInfo|> тега).
    :type strict_subanswers_summarisation_solver: AgentTaskSolver
    :param casual_subanswers_summarisation_solver: Задача суммаризации/объединения независимых ответов на под-вопросы в один финальный ответ (без возможности генерации <|NotEnoughtInfo|> тега).
    :type casual_subanswers_summarisation_solver: AgentTaskSolver
    """
    strict_subanswers_summarisation_solver: AgentTaskSolver
    casual_subanswers_summarisation_solver: AgentTaskSolver


@dataclass
class AnswersAggregatorAgentTasksConfig(BaseAgentTasksConfig):
    """
    :param strict_suba_summarisation: Конфигурация атомарной задачи для LLM-агента по суммаризации/объединению независимых ответов на под-вопросы в один финальный ответ (c возможностью генерации <|NotEnoughtInfo|> тега) на исходный user-вопрос. Значение по умолчанию 'v2'.
    :type strict_suba_summarisation: Union[AgentTaskSolverConfig, str], optional
    :param casual_suba_summarisation: Конфигурация атомарной задачи для LLM-агента по суммаризации/объединению независимых ответов на под-вопросы в один финальный ответ (без возможности генерации <|NotEnoughtInfo|> тега) на исходный user-вопрос. Значение по умолчанию 'v1'.
    :type casual_suba_summarisation: Union[AgentTaskSolverConfig, str], optional
    """
    strict_suba_summarisation: Union[AgentTaskSolverConfig, str] = 'v2'
    casual_suba_summarisation: Union[AgentTaskSolverConfig, str] = 'v1'

    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector] = field(default_factory=lambda: ANSWAGGR_AGENTASKS_SELECTORS_MAPPING)

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = AnswersAggregatorAgentTasksConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config


class AnswersSummBehaviour(Enum):
    strict_answer = 'strict_answer'
    casual_answer = 'casual_answer'
