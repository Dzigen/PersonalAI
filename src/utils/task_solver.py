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
        task_result, status = None, ReturnStatus.success
        self.log("="*20, verbose=self.config.verbose)
        self.log("1. Предобработка данных для их дальнейшней вставки в user-prompt...", verbose=self.config.verbose)

        try:
            formated_context = self.config.formate_context_func(**kwargs)
        except Exception as e:
            self.log(str(e), verbose=self.config.verbose)
            status = ReturnStatus.bad_formater
        else:
            self.log(f"Результат:\n{json.dumps(formated_context, indent=1, ensure_ascii=False)}.", verbose=self.config.verbose)
        finally:
            self.log("Статус: " + STATUS_MESSAGE[status], verbose=self.config.verbose)

        # Если удалось без ошибок привести данных в формат контекста
        # для вставки в user-prompt
        if status == ReturnStatus.success:
            self.log("-"*20, verbose=self.config.verbose)
            self.log("2. Детекция используемого языка...", verbose=self.config.verbose)
            flatten_context = ' '.join(list(formated_context.values()))
            detected_lang, status = detect_lang(flatten_context) if lang == 'auto' else (lang, ReturnStatus.success)

            self.log(f"Результат:\n{detected_lang}.", verbose=self.config.verbose)
            self.log("Статус: " + STATUS_MESSAGE[status], verbose=self.config.verbose)

        # Если удалось определить язык (находится в списке доступных)
        if status == ReturnStatus.success:
            self.log("-"*20, verbose=self.config.verbose)
            self.log("3. Добавление информации в user-prompt...", verbose=self.config.verbose)
            try:
                enriched_user_prompt = self.config.suites[detected_lang].user_prompt.format(**formated_context)
            except Exception as e:
                self.log(str(e), verbose=self.config.verbose)
                status = ReturnStatus.bad_user_prompt_maping
            else:
                self.log(f"Результат:\n{enriched_user_prompt}.", verbose=self.config.verbose)
            finally:
                self.log("Статус: " + STATUS_MESSAGE[status], verbose=self.config.verbose)

        # Если удалось добавить дополнительную инофрмациб в user-prompt
        if status == ReturnStatus.success:
            self.log("-"*20, verbose=self.config.verbose)
            self.log("4. Генерация ответа с помощью LLM-агента.", verbose=self.config.verbose)

            raw_answer = self.agent.generate(
                system_prompt=self.config.suites[detected_lang].system_prompt,
                user_prompt=enriched_user_prompt,
                assistant_prompt=self.config.suites[detected_lang].assistant_prompt)

            self.log(f"Результат:\n{raw_answer}.", verbose=self.config.verbose)
            self.log("Статус: " + STATUS_MESSAGE[status], verbose=self.config.verbose)

        # Если сгенрированная raw-строка не является пустой
        if status == ReturnStatus.success:
            self.log("-"*20, verbose=self.config.verbose)
            self.log("5. Разбор ответа, сгенерированного LLM-агентом.", verbose=self.config.verbose)

            try:
                formated_answer = self.config.suites[detected_lang].parse_answer_func(raw_answer, **kwargs)
            except (KeyError, ValueError) as e:
                self.log(str(e), verbose=self.config.verbose)
                status = ReturnStatus.bad_parser
            finally:
                self.log("Статус: " + STATUS_MESSAGE[status], verbose=self.config.verbose)

        #  Если не было ошибок при разборе raw-строки
        if status == ReturnStatus.success:
            self.log("-"*20, verbose=self.config.verbose)
            self.log("6. Постобработка ответа от LLM-агента.", verbose=self.config.verbose)

            try:
                task_result = self.config.suites[detected_lang].postprocess_answer_func(formated_answer, **kwargs)
            except Exception as e:
                self.log(str(e), verbose=self.config.verbose)
                status = ReturnStatus.bad_postprocessor
            finally:
                self.log("Статус: " + STATUS_MESSAGE[status], verbose=self.config.verbose)

        return task_result, status
