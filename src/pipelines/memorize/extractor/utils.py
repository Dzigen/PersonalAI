from dataclasses import dataclass, field
from typing import Dict, Union
from copy import deepcopy

from .config import MEMEXTRACTOR_AGENTASKS_SELECTORS_MAPPING
from ...utils import BaseTaskSolvers
from ....utils import AgentTaskSolver, AgentTaskSolverConfig, BaseAgentTasksConfig, BaseAgentTaskConfigSelector


@dataclass
class MemExtractorTaskSolvers(BaseTaskSolvers):
    """Набор LLM-задач, осуществляемых в рамках Extractor-стадии Memorize-конвейера.

    :param triplets_extraction_solver: Задачи по извлечению триплетов из текста на естественном языке.
    :type triplets_extraction_solver: AgentTaskSolver
    :param thesises_extraction_solver: Задачи по извлечению тезисной информации из текста на естественном языке.
    :type thesises_extraction_solver: AgentTaskSolver
    """
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
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = MemExtractorAgentTasksConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config
