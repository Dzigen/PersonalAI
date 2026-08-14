from dataclasses import dataclass, field
from typing import Dict, Union
from copy import deepcopy

from .config import CQGEN_AGENTASKS_SELECTORS_MAPPING
from .....utils import BaseTaskSolvers
from ......utils import AgentTaskSolver, AgentTaskSolverConfig, BaseAgentTasksConfig, BaseAgentTaskConfigSelector


@dataclass
class MediumCQGeneratorTaskSolvers(BaseTaskSolvers):
    cluequery_gen_solver: AgentTaskSolver


@dataclass
class ClueQueriesGeneratorAgentTasksConfig(BaseAgentTasksConfig):
    """
    :param plan_initing: Конфигурация атомарной задачи для LLM-агента по генерации clue-запросов. Значение по умолчанию 'v5'.
    :type plan_initing: AgentTaskSolverConfig, optional
    """
    cquerie_generator: Union[AgentTaskSolverConfig, str] = 'v5'

    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector] = field(default_factory=lambda: CQGEN_AGENTASKS_SELECTORS_MAPPING)

    @staticmethod
    def from_dict(dict_config):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = ClueQueriesGeneratorAgentTasksConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config
