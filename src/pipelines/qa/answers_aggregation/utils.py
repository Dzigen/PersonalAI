from dataclasses import dataclass, field
from typing import Dict, Union

from .config import ANSWAGGR_AGENTASKS_SELECTORS_MAPPING
from ...utils import BaseTaskSolvers, BaseAgentTasksConfig, BaseAgentTaskConfigSelector
from ....utils.task_solver import AgentTaskSolver, AgentTaskSolverConfig


@dataclass
class AnswerAggregatorTaskSolvers(BaseTaskSolvers):
    subanswers_summarisation_solver: AgentTaskSolver


@dataclass
class AnswersAggregatorAgentTasksConfig(BaseAgentTasksConfig):
    """
    :param suba_summarisation: Конфигурация атомарной задачи для LLM-агента по суммаризации/объединению независимых ответов на под-вопросы в один финальный ответ на исходный user-вопрос. Значение по умолчанию 'v1'.
    :type suba_summarisation: AgentTaskSolverConfig, optional
    """
    suba_summarisation: Union[AgentTaskSolverConfig, str] = 'v1'

    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector] = field(default_factory=lambda: ANSWAGGR_AGENTASKS_SELECTORS_MAPPING)

    @staticmethod
    def from_dict(dict_config):
        formated_config = AnswersAggregatorAgentTasksConfig(**dict_config)
        formated_config.formate_fields()
        return formated_config
