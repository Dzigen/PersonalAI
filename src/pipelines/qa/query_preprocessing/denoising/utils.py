from dataclasses import dataclass, field
from typing import Dict, Union

from .config import QUERYDENOIS_AGENTASKS_SELECTORS_MAPPING
from ....utils import BaseTaskSolvers, BaseAgentTasksConfig, BaseAgentTaskConfigSelector
from .....utils.task_solver import AgentTaskSolver, AgentTaskSolverConfig


@dataclass
class QueryDenoiserTaskSolvers(BaseTaskSolvers):
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
    def from_dict(dict_config):
        formated_config = QueryDenoiserAgentTasksConfig(**dict_config)
        formated_config.formate_fields()
        return formated_config
