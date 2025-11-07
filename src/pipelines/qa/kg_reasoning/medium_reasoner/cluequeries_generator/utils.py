from dataclasses import dataclass, field
from typing import Dict, Union

from .config import CQGEN_AGENTASKS_SELECTORS_MAPPING
from .....utils import BaseTaskSolvers, BaseAgentTaskConfigSelector, BaseAgentTasksConfig
from ......utils import AgentTaskSolver, AgentTaskSolverConfig


@dataclass
class MediumCQGeneratorTaskSolvers(BaseTaskSolvers):
    cluequery_gen_solver: AgentTaskSolver


@dataclass
class ClueQueriesGeneratorAgentTasksConfig(BaseAgentTasksConfig):
    """
    :param plan_initing: Конфигурация атомарной задачи для LLM-агента по генерации clue-запросов. Значение по умолчанию 'v1'.
    :type plan_initing: AgentTaskSolverConfig, optional
    """
    cquerie_generator: Union[AgentTaskSolverConfig, str] = 'v1'

    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector] = field(default_factory=lambda: CQGEN_AGENTASKS_SELECTORS_MAPPING)

    @staticmethod
    def from_dict(dict_config):
        formated_config = ClueQueriesGeneratorAgentTasksConfig(**dict_config)
        formated_config.formate_fields()
        return formated_config
