from dataclasses import dataclass, field
from typing import Dict, Union
from copy import deepcopy

from .config import NODESTREEM_AGENTASKS_SELECTORS_MAPPING
from ...pipelines.utils import BaseTaskSolvers, BaseAgentTasksConfig, BaseAgentTaskConfigSelector
from ...utils.task_solver import AgentTaskSolver, AgentTaskSolverConfig


@dataclass
class NodesTreeModelTaskSolvers(BaseTaskSolvers):
    """Набор решателей задач, используемых в NodesTree-модели.

    :param nodes_summarization_solver: Решатель атомарной задачи по суммаризации информации (вершин) из дерева.
    :type nodes_summarization_solver: AgentTaskSolver
    """
    nodes_summarization_solver: AgentTaskSolver


@dataclass
class NodesTreeModelAgentTasksConfig(BaseAgentTasksConfig):
    """
    :param nodes_summarization: Конфигурация атомарной задачи для LLM-агента по резюмированию/суммаризации текстовых полей у заданного набора leaf-объектов (object-вершин) из дерева. Значение по умолчанию DEFAULT_SUMMN_TASK_CONFIG.
    :type nodes_summarization: AgentTaskSolverConfig, optional
    :param task_to_selector_mapping: Отображение идентификаторов задач в соответствующие селекторы конфигураций.
    :type task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector]
    """
    nodes_summarization: Union[AgentTaskSolverConfig, str] = 'v1'

    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector] = field(default_factory=lambda: NODESTREEM_AGENTASKS_SELECTORS_MAPPING)

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = NodesTreeModelAgentTasksConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config
