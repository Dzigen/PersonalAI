from dataclasses import dataclass, field
from typing import Dict, Union
from copy import deepcopy

from .config import SPENH_AGENTASKS_SELECTORS_MAPPING
from .....utils import BaseTaskSolvers, BaseAgentTasksConfig, BaseAgentTaskConfigSelector
from ......utils import AgentTaskSolver, AgentTaskSolverConfig


@dataclass
class MediumPlanEnhancerTaskSolvers(BaseTaskSolvers):
    plan_initialing_solver: AgentTaskSolver
    enhance_classify_solver: AgentTaskSolver
    plan_enhancing_solver: AgentTaskSolver


@dataclass
class SearchPlanEnhancerAgentTasksConfig(BaseAgentTasksConfig):
    """
    :param plan_initing: Конфигурация атомарной задачи для LLM-агента по генерации базового/стартового плана поиска. Значение по умолчанию 'v2'.
    :type plan_initing: AgentTaskSolverConfig, optional
    :param enhance_classifier: Конфигурация атомарной задачи для LLM-агента по определению необходимости (бинарная классификация) модификации существующего плана поиска. Значение по умолчанию 'v2'.
    :type enhance_classifier: AgentTaskSolverConfig, optional
    :param plan_enhancing: Конфигурация атомарной задачи для LLM-агента по подификации/перегенерации не пройденных шагов поиска в рамках существующего плана. Значение по умолчанию 'v2'.
    :type plan_enhancing: AgentTaskSolverConfig, optional
    """
    plan_initing: Union[AgentTaskSolverConfig, str] = 'v2'
    enhance_classifier: Union[AgentTaskSolverConfig, str] = 'v2'
    plan_enhancing: Union[AgentTaskSolverConfig, str] = 'v2'

    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector] = field(default_factory=lambda: SPENH_AGENTASKS_SELECTORS_MAPPING)

    @staticmethod
    def from_dict(dict_config):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = SearchPlanEnhancerAgentTasksConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config
