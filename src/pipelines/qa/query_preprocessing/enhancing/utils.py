from dataclasses import dataclass, field
from typing import Dict, Union
from copy import deepcopy

from .config import QUERYENH_AGENTASKS_SELECTORS_MAPPING
from ....utils import BaseTaskSolvers
from .....utils.task_solver import AgentTaskSolver, AgentTaskSolverConfig, BaseAgentTasksConfig, BaseAgentTaskConfigSelector


@dataclass
class QueryEnhancerTaskSolvers(BaseTaskSolvers):
    """Набор атомарных LLM-задач, осуществляемых рамках в QueryEnhancer.

    :param queryexpansion_solver: Задача по расширению исходного запроса.
    :type queryexpansion_solver: AgentTaskSolver
    :param termscheck_solver: Задача по проверке и конкретизации терминов в исходном запросе.
    :type termscheck_solver: AgentTaskSolver
    :param linguistcheck_solver: Задача по лингвистической проверке и перефразированию исходного запроса.
    :type linguistcheck_solver: AgentTaskSolver
    """
    queryexpansion_solver: AgentTaskSolver
    termscheck_solver: AgentTaskSolver
    linguistcheck_solver: AgentTaskSolver


@dataclass
class QueryEnhancerAgentTasksConfig(BaseAgentTasksConfig):
    """
    :param qexpan: Конфигурация атомарной задачи для LLM-агента по добавлению более понятных языковых конструкций в запрос. Значение по умолчанию 'v2'.
    :type qexpan: Union[AgentTaskSolverConfig, str], optional
    :param termscheck: Конфигурация атомарной задачи для LLM-агента по замене слабоопределённых фраз в запросе на конкретные термины. Значение по умолчанию 'v2'.
    :type termscheck: Union[AgentTaskSolverConfig, str], optional
    :param lingcheck: Конфигурация атомарной задачи для LLM-агента по перефразированию запроса с соблюдением грамматики и синтаксиса используемого естественного языка. Значение по умолчанию 'v1'.
    :type lingcheck: Union[AgentTaskSolverConfig, str], optional
    """
    qexpan: Union[AgentTaskSolverConfig, str] = 'v2'
    termscheck: Union[AgentTaskSolverConfig, str] = 'v2'
    lingcheck: Union[AgentTaskSolverConfig, str] = 'v1'

    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector] = field(default_factory=lambda: QUERYENH_AGENTASKS_SELECTORS_MAPPING)

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = QueryEnhancerAgentTasksConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config
