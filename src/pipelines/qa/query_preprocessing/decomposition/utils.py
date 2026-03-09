from dataclasses import dataclass, field
from typing import Dict, Union
from copy import deepcopy

from .config import QUERYDECOMP_AGENTASKS_SELECTORS_MAPPING
from ....utils import BaseTaskSolvers
from .....utils.task_solver import AgentTaskSolver, AgentTaskSolverConfig, BaseAgentTasksConfig, BaseAgentTaskConfigSelector


@dataclass
class QueryDecomposerTaskSolvers(BaseTaskSolvers):
    """Набор атомарных LLM-задач, осуществляемых рамках в QueryDecomposer.

    :param decompose_classifier_solver: Задача по классификации на предмет необходимости декомпозиции исходного вопроса.
    :type decompose_classifier_solver: AgentTaskSolver
    :param q_decomposition_solver: Задача по разбиению вопроса на независимые простые под-вопросы.
    :type q_decomposition_solver: AgentTaskSolver
    """
    decompose_classifier_solver: AgentTaskSolver
    q_decomposition_solver: AgentTaskSolver


@dataclass
class QueryDecomposerAgentTasksConfig(BaseAgentTasksConfig):
    """
    :param classify: Конфигурация атомарной задачи для LLM-агента по классификации наличия независимых запросов (составности/сложности) в user-вопросе. Значение по умолчанию 'v2'.
    :type classify: Union[AgentTaskSolverConfig, str], optional
    :param decompose: Конфигурация атомарной задачи для LLM-агента по разбиению user-вопроса на независимые/простые под-вопросы. Значение по умолчанию 'v2'.
    :type decompose: Union[AgentTaskSolverConfig, str], optional
    """
    classify: Union[AgentTaskSolverConfig, str] = 'v2'
    decompose: Union[AgentTaskSolverConfig, str] = 'v2'

    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector] = field(default_factory=lambda: QUERYDECOMP_AGENTASKS_SELECTORS_MAPPING)

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = QueryDecomposerAgentTasksConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config
