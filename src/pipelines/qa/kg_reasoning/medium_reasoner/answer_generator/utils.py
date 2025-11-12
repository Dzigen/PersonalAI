from dataclasses import dataclass, field
from typing import Dict, Union
from copy import deepcopy

from .config import ANSWGEN_AGENTASKS_SELECTORS_MAPPING
from .....utils import BaseTaskSolvers, BaseAgentTasksConfig, BaseAgentTaskConfigSelector
from ......utils import AgentTaskSolver, AgentTaskSolverConfig


@dataclass
class MediumAGeneratorTaskSolvers(BaseTaskSolvers):
    answer_classify_solver: AgentTaskSolver
    answer_gen_solver: AgentTaskSolver


@dataclass
class AnswerGeneratorAgentTasksConfig(BaseAgentTasksConfig):
    """
    :param answer_classifier: Конфигурация атомарной задачи для LLM-агента по определению наличия необходимой информации для генерации релевантного ответа на вопрос. Значение по умолчанию 'v1'.
    :type answer_classifier: AgentTaskSolverConfig, optional
    :param answer_generator: Конфигурация атомарной задачи для LLM-агента по выполнению условной генарции овтета на заданный user-вопрос. Значение по умолчанию 'v1'.
    :type answer_generator: AgentTaskSolverConfig, optional
    """
    answer_classifier: Union[AgentTaskSolverConfig, str] = 'v1'
    answer_generator: Union[AgentTaskSolverConfig, str] = 'v1'

    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector] = field(default_factory=lambda: ANSWGEN_AGENTASKS_SELECTORS_MAPPING)

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = AnswerGeneratorAgentTasksConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config
