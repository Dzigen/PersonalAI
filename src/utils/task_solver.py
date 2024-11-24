from dataclasses import dataclass, field
from typing import List, Union, Tuple, Dict

from .logger import Logger
from .language_detector import detect_lang
from .errors import ReturnInfo, ReturnStatus, NOT_SUPPORTED_LANG_MSG
from ..agents.utils import AbstractAgentConnector

@dataclass
class AgentTaskSuite:
    system_prompt: str
    user_prompt: str
    assistant_prompt: str
    parse_answer_func: object
    postprocess_answer_func: object

@dataclass
class AgentTaskSolverConfig:
    suites: Dict[str, AgentTaskSuite]
    formate_context_func: object
    log: Logger
    verbose: bool = False

class AgentTaskSolver:

    def __init__(self, agent: AbstractAgentConnector, config: AgentTaskSolverConfig) -> None:
        self.config = config
        self.agent = agent
        self.log = self.config.log

    def solve(self, lang: str = 'auto', **kwargs) -> Union[object, ReturnInfo]:
        info = ReturnInfo()

        formated_context = self.config.formate_context_func(**kwargs)
        flatten_context = ' '.join(list(formated_context.items()))

        detected_lang, status = detect_lang(flatten_context) if lang == 'auto' else (lang, ReturnStatus.success)

        # TODO: Не удалось определить язык

        enriched_user_prompt = self.config.suites[detected_lang].user_prompt.format(**formated_context)

        raw_answer = self.agent.generate(
            system_prompt=self.config.suites[detected_lang].system_prompt,
            user_prompt=enriched_user_prompt,
            assistant_prompt=self.config.suites[detected_lang].assistant_prompt)
        self.log("Raw agent answer: " + raw_answer, verbose=self.config.verbose)

        # TODO: пустая raw-строка

        formated_answer = self.config.suites[detected_lang].parse_answer_func(formated_answer, **kwargs)
        self.log("Formated agent answer: " + str(formated_answer), verbose=self.config.verbose)

        task_result = self.config.suites[detected_lang].postprocess_answer_func(formated_answer, **kwargs)
        self.log("Task reulst: " + str(task_result), verbose=self.config.verbose)

        return task_result, info
