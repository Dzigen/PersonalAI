from dataclasses import dataclass, field
from typing import Dict, Union
from copy import deepcopy

from .config import ENTEXTR_AGENTASKS_SELECTORS_MAPPING
from .....utils import BaseTaskSolvers
from ......utils import AgentTaskSolver, AgentTaskSolverConfig, BaseAgentTasksConfig, BaseAgentTaskConfigSelector


@dataclass
class MediumEntitiesExtractorTaskSolvers(BaseTaskSolvers):
    entities_extractor_solver: AgentTaskSolver


@dataclass
class EntitiesExtractorAgentTasksConfig(BaseAgentTasksConfig):
    """
    :param entities_extraction: Конфигурация атомарной задачи для LLM-агента по извлечению сущностей из поискового запроса. Значение по умолчанию 'v1'.
    :type entities_extraction: AgentTaskSolverConfig, optional
    """
    entities_extraction: Union[AgentTaskSolverConfig, str] = 'v1'

    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector] = field(default_factory=lambda: ENTEXTR_AGENTASKS_SELECTORS_MAPPING)

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = EntitiesExtractorAgentTasksConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config
