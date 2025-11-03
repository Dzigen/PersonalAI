from dataclasses import dataclass, field
from typing import Union, Dict

from .agent_tasks.thesis_extraction import AgentThesisExtrTaskConfigSelector
from .agent_tasks.triplet_extraction import AgentTripletExtrTaskConfigSelector
from ...utils import BaseAgentTasksConfig, BaseAgentTaskConfigSelector
from ....utils import AgentTaskSolverConfig

MEM_EXTRACTOR_MAIN_LOG_PATH = "log/memorize/extractor/main"

MEMEXTRACTOR_AGENTASKS_SELECTORS_MAPPING: Dict[str, BaseAgentTaskConfigSelector] = {
    'triplets_extraction': AgentTripletExtrTaskConfigSelector,
    'thesises_extraction': AgentThesisExtrTaskConfigSelector
}

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

    