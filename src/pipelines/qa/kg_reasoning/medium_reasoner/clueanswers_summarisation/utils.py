from dataclasses import dataclass, field
from typing import Dict, Union

from .config import CQSUMM_AGENTASKS_SELECTORS_MAPPING
from .....utils import BaseTaskSolvers, BaseAgentTasksConfig, BaseAgentTaskConfigSelector
from ......utils import AgentTaskSolver, AgentTaskSolverConfig


@dataclass
class MediumASummarizerTaskSolvers(BaseTaskSolvers):
    clueanswers_summ_solver: AgentTaskSolver

@dataclass
class ClueAnswersSummarizerAgentTasksConfig(BaseAgentTasksConfig):
    """
    :param canswers_summarisation: Конфигурация атомарной задачи для LLM-агента по резюмированию информации, извлечённой из графа знаний по заданному search_query-шагу поиска. Значение по умолчанию 'v1'.
    :type canswers_summarisation: AgentTaskSolverConfig, optional
    """
    canswers_summarisation: Union[AgentTaskSolverConfig, str] = 'v1'

    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector] = field(default_factory=lambda: CQSUMM_AGENTASKS_SELECTORS_MAPPING)