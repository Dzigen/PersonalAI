from dataclasses import dataclass, field
from typing import List, Union, Tuple, Dict
import json

from .logger import Logger
from .language_detector import detect_lang
from .errors import ReturnInfo, ReturnStatus, STATUS_MESSAGE
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

    def solve(self, lang: str = 'auto', **kwargs) -> Tuple[object, ReturnStatus]:
        status = ReturnStatus.success
        self.log("="*20, verbose=self.config.verbose)
        self.log("1. Предобработка данных для их дальнейшней вставки в user-prompt...", verbose=self.config.verbose)

        try:
            formated_context = self.config.formate_context_func(**kwargs)
        except Exception:
            status = ReturnStatus.bad_formater

        self.log(f"Результат:\n{json.dump(formated_context, indent=1, ensure_ascii=False)}.", verbose=self.config.verbose)
        self.log("Статус: " + STATUS_MESSAGE[status], verbose=self.config.verbose)

        # Если удалось без ошибок привести данных в формат контекста
        # для вставки в user-prompt
        if status == ReturnStatus.success:
            self.log("-"*20, verbose=self.config.verbose)
            self.log("2. Детекция используемого языка...", verbose=self.config.verbose)
            flatten_context = ' '.join(list(formated_context.items()))
            detected_lang, status = detect_lang(flatten_context) if lang == 'auto' else (lang, ReturnStatus.success)

            self.log(f"Результат:\n{detected_lang}.", verbose=self.config.verbose)
            self.log("Статус: " + STATUS_MESSAGE[status], verbose=self.config.verbose)

        # Если удалось определить язык (находится в списке доступных)
        if status == ReturnStatus.success:
            self.log("-"*20, verbose=self.config.verbose)
            self.log("3. Генерация ответа с помощью LLM-агента.", verbose=self.config.verbose)

            enriched_user_prompt = self.config.suites[detected_lang].user_prompt.format(**formated_context)

            raw_answer = self.agent.generate(
                system_prompt=self.config.suites[detected_lang].system_prompt,
                user_prompt=enriched_user_prompt,
                assistant_prompt=self.config.suites[detected_lang].assistant_prompt)

            self.log(f"Результат:\n{raw_answer}.", verbose=self.config.verbose)
            self.log("Статус: " + STATUS_MESSAGE[status], verbose=self.config.verbose)

        # Если сгенрированная raw-строка не является пустой
        if status == ReturnStatus.success:
            self.log("-"*20, verbose=self.config.verbose)
            self.log("4. Разбор ответа, сгенерированного LLM-агентом.", verbose=self.config.verbose)

            try:
                formated_answer, status = self.config.suites[detected_lang].parse_answer_func(raw_answer, **kwargs)
            except Exception:
                status = ReturnStatus.bad_parser

            self.log("Статус: " + STATUS_MESSAGE[status], verbose=self.config.verbose)

        #  Если не было ошибок при разборе raw-строки
        if status == ReturnStatus.success:
            self.log("-"*20, verbose=self.config.verbose)
            self.log("5. Постобработка ответа от LLM-агента.", verbose=self.config.verbose)

            try:
                task_result, status = self.config.suites[detected_lang].postprocess_answer_func(formated_answer, **kwargs)
            except Exception:
                status = ReturnStatus.bad_postprocessor

            self.log("Статус: " + STATUS_MESSAGE[status], verbose=self.config.verbose)

        return task_result, status
