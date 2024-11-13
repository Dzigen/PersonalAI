from typing import List, Tuple
from dataclasses import dataclass, field

from .utils import QA_USER_PROMPT, QA_SYSTEM_PROMPT, QA_LOG_PATH, ANSWER_PARSE_FUNC
from ...utils.data_structs import Triplet
from ...agents import AgentDriver, AgentDriverConfig
from ...utils.data_structs import TripletCreator
from ...utils.data_structs import RelationType
from ...utils import Logger, detect_lang, ReturnInfo, ReturnStatus
from ...utils.errors import QA_BAD_QA_PROMPT_MSG, QA_EMPTY_ANSWER_MSG, NOT_SUPPORTED_LANG_MSG

@dataclass
class QALLMGeneratorConfig:
    #: Язык, который будет использоваться в подаваемом на вход тексте. На основании выбранного языка будут использоваться соответствующие промпты. Если 'auto', то язык определяется автоматически.
    lang: str = "auto"
    system_prompt: dict = field(default_factory=lambda: QA_SYSTEM_PROMPT)
    user_prompt: dict = field(default_factory=lambda: QA_USER_PROMPT)
    answer_parse_func: dict = field(default_factory=lambda: ANSWER_PARSE_FUNC)
    #: Конфигурация LLM-агента, который будет использоваться в рамках данной стадии
    agent_cofig: AgentDriverConfig = field(default_factory=lambda: AgentDriverConfig())
    #: Типы триплетов, которые могут присутствовать в контексте для генерации ответа на user-вопрос
    relation_type: List[RelationType] = field(default_factory=lambda: [RelationType.simple, RelationType.hyper, RelationType.episodic])
    #
    log: Logger = field(default_factory=lambda: Logger(QA_LOG_PATH))
    verbose: bool = False

class QALLMGenerator:
    """Верхнеуровневый класс четвёртой стадии QA-конвейера для генерации ответа на user-вопрос,
    обусловленного извлёчённой информацией из памяти (графа знаний) ассистента.
    """
    def __init__(self, config: QALLMGeneratorConfig = QALLMGeneratorConfig()) -> None:
        self.config = config
        self.agent = AgentDriver.connect(config.agent_cofig)
        self.log = self.config.log

    def formate_context(self, triplets: List[Triplet]) -> str:
        """Метод предназначен для предтсавления набора триплетов
        в виде ненумерованного списка с их строковыми представлениями на естественном языке.

        :param triplets: Набор триплетов.
        :type triplets: List[Triplet]
        :return: Ненумепованный список со строковыми представлениями триплетов.
        :rtype: str
        """
        filtered_context = list(map(lambda triplet: f"- {(TripletCreator.stringify(triplet)[1] if triplet.stringified is None else triplet.stringified).strip()}", triplets))
        return "\n".join(filtered_context)

    def generate(self, query: str, context: str) -> Tuple[str, ReturnInfo]:
        """Метод предназначен для условной генерации ответа на вопрос.

        :param query: Вопрос на естественном языке.
        :type query: str
        :param context: Ненумерованный список дополнительной информации на естественном языке.
        :type context: str
        :return: Кортеж из двух объектов: (1) сгенерированнвй ответ на вопрос; (2) статус выполнения операции с пояснительной информацией.
        :rtype: Tuple[str, ReturnInfo]
        """
        answer, info = '', ReturnInfo()
        detected_lang, status = detect_lang(query) if self.config.lang == 'auto' else (self.config.lang, ReturnStatus.success)
        self.log(f"DETECTED LANG: {detected_lang}", verbose=self.config.verbose)
        if status == ReturnStatus.not_supported_lang:
            self.log(NOT_SUPPORTED_LANG_MSG, verbose=self.config.verbose)
            info.occurred_warning.append(status)

        if status == ReturnStatus.success:
            formated_input = self.config.user_prompt[detected_lang].format(q=query, c=context)

            raw_output = self.agent.generate(
                system_prompt=self.config.system_prompt[detected_lang],
                user_prompt=formated_input).strip()
            self.log(f"RAW_ANSWER: {raw_output}", verbose=self.config.verbose)

            answer, status = self.config.answer_parse_func[detected_lang](raw_output)
            self.log(f"PARSED_ANSWER: {answer}", verbose=self.config.verbose)
            if status == ReturnStatus.bad_format:
                self.log(QA_BAD_QA_PROMPT_MSG, verbose=self.config.verbose)
                info.occurred_warning.append(status)

        if len(answer) == 0:
            info.status = ReturnStatus.empty_answer
            info.message = QA_EMPTY_ANSWER_MSG

        return answer, info
