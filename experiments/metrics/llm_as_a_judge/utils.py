from dataclasses import dataclass, field
from typing import Dict, Union
from copy import deepcopy
from ..utils.task_solver import BaseAgentTasksConfig, AgentTaskSolverConfig, BaseAgentTaskConfigSelector
from .configs import JUDGE_AGENTASKS_SELECTORS_MAPPING

@dataclass
class LLMasaJudgeAgentTasksConfig(BaseAgentTasksConfig):

    llmasajudge: Union[AgentTaskSolverConfig, str] = 'v1'

    task_to_selector_mapping: Dict[str, BaseAgentTaskConfigSelector] = \
        field(default_factory=lambda: JUDGE_AGENTASKS_SELECTORS_MAPPING)

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = LLMasaJudgeAgentTasksConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config