from dataclasses import dataclass, field
from typing import Dict, Union

from .config import QUERYDECOMP_AGENTASKS_SELECTORS_MAPPING
from ....utils import BaseTaskSolvers, BaseAgentTasksConfig, BaseAgentTaskConfigSelector
from .....utils.task_solver import AgentTaskSolver, AgentTaskSolverConfig


@dataclass
class QueryDecomposerTaskSolvers(BaseTaskSolvers):
    decompose_classifier_solver: AgentTaskSolver
    q_decomposition_solver: AgentTaskSolver


@dataclass
class QueryDecomposerAgentTasksConfig(BaseAgentTasksConfig):
    """
    :param classify: Конфигурация атомарной задачи для LLM-агента по классификации наличия независимых запросов (составности/сложности) в user-вопросе. Значение по умолчанию 'v1'.
    :type classify: AgentTaskSolverConfig, optional
    :param decompose: Конфигурация атомарной задачи для LLM-агента по разбиению user-вопроса на независимые/простые под-вопросы. Значение по умолчанию 'v1'.
    :type decompose: AgentTaskSolverConfig, optional
    """
    classify: Union[AgentTaskSolverConfig, str] = 'v1'
    decompose: Union[AgentTaskSolverConfig, str] = 'v1'

    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector] = field(default_factory=lambda: QUERYDECOMP_AGENTASKS_SELECTORS_MAPPING)

    @staticmethod
    def from_dict(dict_config):
        formated_config = QueryDecomposerAgentTasksConfig(**dict_config)
        formated_config.formate_fields()
        return formated_config
