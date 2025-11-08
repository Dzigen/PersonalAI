from dataclasses import dataclass, field
from typing import Dict, Union

from .config import MEMEXTRACTOR_AGENTASKS_SELECTORS_MAPPING
from ...utils import BaseTaskSolvers, BaseAgentTaskConfigSelector, BaseAgentTasksConfig
from ....utils import AgentTaskSolver, AgentTaskSolverConfig


@dataclass
class MemExtractorTaskSolvers(BaseTaskSolvers):
    triplets_extraction_solver: AgentTaskSolver
    thesises_extraction_solver: AgentTaskSolver


@dataclass
class MemExtractorAgentTasksConfig(BaseAgentTasksConfig):
    """
    :param triplets_extraction: Конфигурация атомарной задачи для LLM-агента по извлечению триплетов с информацией типа 'simple' из слабоструктурированных текстов на естественном языке. Значение по умолчанию 'v2'.
    :type triplets_extraction: Union[AgentTaskSolverConfig, str]
    :param thesises_extraction: Конфигурация атомарной задачи для LLM-агента по извлечению триплетов с информацией типа 'hyper' из слабоструктурированных текстов на естественном языке. Значение по умолчанию 'v2'.
    :type thesises_extraction: Union[AgentTaskSolverConfig, str]
    """
    triplets_extraction: Union[AgentTaskSolverConfig, str] = 'v2'
    thesises_extraction: Union[AgentTaskSolverConfig, str] = 'v2'

    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector] = field(default_factory=lambda: MEMEXTRACTOR_AGENTASKS_SELECTORS_MAPPING)

    @staticmethod
    def from_dict(dict_config):
        formated_config = MemExtractorAgentTasksConfig(**dict_config)
        formated_config.formate_fields()
        return formated_config
