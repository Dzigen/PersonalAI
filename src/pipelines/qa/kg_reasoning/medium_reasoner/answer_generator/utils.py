from dataclasses import dataclass, field
from typing import Dict, Union
from copy import deepcopy

from .config import ANSWGEN_AGENTASKS_SELECTORS_MAPPING
from .....utils import BaseTaskSolvers
from ......utils import AgentTaskSolver, AgentTaskSolverConfig, BaseAgentTasksConfig, BaseAgentTaskConfigSelector


@dataclass
class MediumAGeneratorTaskSolvers(BaseTaskSolvers):
    answer_classify_solver: AgentTaskSolver
    strict_answer_gen_solver: AgentTaskSolver
    casual_answer_gen_solver: AgentTaskSolver


@dataclass
class AnswerGeneratorAgentTasksConfig(BaseAgentTasksConfig):
    """
    :param answer_classifier: Конфигурация атомарной задачи для LLM-агента по определению наличия необходимой информации для генерации релевантного ответа на вопрос. Значение по умолчанию 'v2'.
    :type answer_classifier: AgentTaskSolverConfig, optional
    :param strict_answer_generator: Конфигурация атомарной задачи для LLM-агента по выполнению строгой условной генерации овтета (с возможностью генерации <|NotEnoughtInfo|> тега) на заданный user-вопрос. Значение по умолчанию 'v3'.
    :type strict_answer_generator: AgentTaskSolverConfig, optional
    :param casual_answer_generator: Конфигурация атомарной задачи для LLM-агента по выполнению нестрогой условной генерации овтета (без возможности генерации <|NotEnoughtInfo|> тега) на заданный user-вопрос. Значение по умолчанию 'v1'.
    :type casual_answer_generator: AgentTaskSolverConfig, optional
    """
    answer_classifier: Union[AgentTaskSolverConfig, str] = 'v2'
    strict_answer_generator: Union[AgentTaskSolverConfig, str] = 'v3'
    casual_answer_generator: Union[AgentTaskSolverConfig, str] = 'v1'

    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector] = field(default_factory=lambda: ANSWGEN_AGENTASKS_SELECTORS_MAPPING)

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = AnswerGeneratorAgentTasksConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config
