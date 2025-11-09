from dataclasses import dataclass, field
from typing import Dict, Union
from copy import deepcopy

from .config import CAGEN_AGENTASKS_SELECTORS_MAPPING
from .....utils import BaseTaskSolvers, BaseAgentTasksConfig, BaseAgentTaskConfigSelector
from ......utils import AgentTaskSolver, AgentTaskSolverConfig


@dataclass
class MediumCAGeneratorTaskSolvers(BaseTaskSolvers):
    cagen_solver: AgentTaskSolver


@dataclass
class ClueAnswerGeneratorAgentTasksConfig(BaseAgentTasksConfig):
    """
    :param cagen: Конфигурация атомарной задачи для LLM-агента по резюмированию информации, извлечённой по заданному clue-заросу из графа знаний. Значение по умолчанию 'v1'.
    :type cagen: AgentTaskSolverConfig, optional
    """
    cagen: Union[AgentTaskSolverConfig, str] = 'v1'

    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector] = field(default_factory=lambda: CAGEN_AGENTASKS_SELECTORS_MAPPING)

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = ClueAnswerGeneratorAgentTasksConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config
