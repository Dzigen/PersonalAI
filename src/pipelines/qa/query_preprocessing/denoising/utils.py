from dataclasses import dataclass, field
from typing import Dict, Union
from copy import deepcopy

from .config import QUERYDENOIS_AGENTASKS_SELECTORS_MAPPING
from ....utils import BaseTaskSolvers, BaseAgentTasksConfig, BaseAgentTaskConfigSelector
from .....utils.task_solver import AgentTaskSolver, AgentTaskSolverConfig


@dataclass
class QueryDenoiserTaskSolvers(BaseTaskSolvers):
    """Набор атомарных LLM-задач, осуществляемых в рамках QueryDenoiser.

    :param swremoval_solver: Задача по удалению стоп-слов и лишней информации.
    :type swremoval_solver: AgentTaskSolver
    :param grammar_check_solver: Задача по грамматической проверке и исправлению запроса.
    :type grammar_check_solver: AgentTaskSolver
    """
    swremoval_solver: AgentTaskSolver
    grammar_check_solver: AgentTaskSolver


@dataclass
class QueryDenoiserAgentTasksConfig(BaseAgentTasksConfig):
    """
    :param swremoval: Конфигурация атомарной задачи для LLM-агента по удалению излишней/ненужной информации из запроса. Значение по умолчанию 'v1'.
    :type swremoval: AgentTaskSolverConfig, optional
    :param grammarcheck: Конфигурация атомарной задачи для LLM-агента по корректировке/переформулированию запроса в соответствии с грамматикой и синтаксисом используемого естественного языка. Значение по умолчанию 'v1'.
    :type grammarcheck: AgentTaskSolverConfig, optional
    """
    swremoval: Union[AgentTaskSolverConfig, str] = 'v1'
    grammarcheck: Union[AgentTaskSolverConfig, str] = 'v1'

    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector] = field(default_factory=lambda: QUERYDENOIS_AGENTASKS_SELECTORS_MAPPING)

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = QueryDenoiserAgentTasksConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config
