from dataclasses import dataclass, field
from typing import Dict, Union

from .agent_tasks.replace_simple_triplets import AgentReplSimpleTripletTaskConfigSelector
from .agent_tasks.replace_thesis_triplets import AgentReplThesisTripletTaskConfigSelector
from ...utils import BaseAgentTasksConfig, BaseAgentTaskConfigSelector
from ....utils import AgentTaskSolverConfig

MEM_UPDATOR_MAIN_LOG_PATH = "log/memorize/updator/main"

MEMUPDATOR_AGENTASKS_SELECTORS_MAPPING: Dict[str, BaseAgentTaskConfigSelector] = {
    'replace_simple': AgentReplSimpleTripletTaskConfigSelector,
    'replace_thesis': AgentReplThesisTripletTaskConfigSelector
}

@dataclass
class MemUpdatorAgentTasksConfig(BaseAgentTasksConfig):
    """
    :param replace_simple_task_config: Конфигурация атомарной задачи для LLM-агента по поиску устаревших триплетов типа "simple". Значение по умолчанию 'v1'.
    :type replace_simple_task_config: AgentTaskSolverConfig, optional
    :param replace_thesis_task_config: Конфигурация атомарной задачи для LLM-агента по поиску устаревших триплетов типа "hyper". Значение по умолчанию 'v1'.
    :type replace_thesis_task_config: AgentTaskSolverConfig, optional
    """
    replace_simple: Union[AgentTaskSolverConfig, str] = 'v1'
    replace_thesis: Union[AgentTaskSolverConfig, str] = 'v1'

    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector] = field(default_factory=lambda: MEMUPDATOR_AGENTASKS_SELECTORS_MAPPING)