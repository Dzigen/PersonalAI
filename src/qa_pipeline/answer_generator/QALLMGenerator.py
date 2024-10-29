from typing import List, Tuple
from dataclasses import dataclass, field

from .utils import QA_USER_PROMPT, QA_SYSTEM_PROMPT, QA_LOG_PATH, ANSWER_PARSE_FUNC
from ...utils.data_structs import Triplet
from ...agents import AgentDriver, AgentDriverConfig
from ...utils.data_structs import TripletCreator
from ...utils.data_structs import RelationType
from ...utils import Logger, detect_lang, ReturnInfo, ReturnStatus
from ...utils.errors import QA_BAD_QA_PROMPT, QA_EMPTY_ANSWER

@dataclass
class QALLMGeneratorConfig:
    """_summary_
    """
    #
    lang: str = "auto"
    system_prompt: dict = field(default_factory=lambda: QA_SYSTEM_PROMPT)
    user_prompt: dict = field(default_factory=lambda: QA_USER_PROMPT)
    answer_parse_func: dict = field(default_factory=lambda: ANSWER_PARSE_FUNC)
    #
    agent_cofig: AgentDriverConfig = field(default_factory=lambda: AgentDriverConfig())
    #
    relation_type: List[RelationType] = field(default_factory=lambda: [RelationType.simple, RelationType.hyper, RelationType.episodic])
    #
    log: Logger = field(default_factory=lambda: Logger(QA_LOG_PATH))
    verbose: bool = False

class QALLMGenerator:
    """Главный класс для генерации ответов по пользовательским вопросам на основе
    извлечённой информации из графа знаний
    """
    def __init__(self, config: QALLMGeneratorConfig = QALLMGeneratorConfig()) -> None:
        """_summary_

        :param config: _description_, defaults to QALLMGeneratorConfig()
        :type config: QALLMGeneratorConfig, optional
        """
        self.config = config
        self.agent = AgentDriver.connect(config.agent_cofig)
        self.log = self.config.log

    def formate_context(self, triplets: List[Triplet]) -> str:
        """_summary_

        :param triplets: _description_
        :type triplets: List[Triplet]
        :return: _description_
        :rtype: str
        """
        filtered_context = list(map(lambda triplet: f"- {TripletCreator.stringify(triplet)[1] if triplet.stringified is None else triplet.stringified}", triplets))
        return "\n".join(filtered_context)

    def generate(self, query: str, context: str) -> Tuple[str, ReturnInfo]:
        """_summary_

        :param query: _description_
        :type query: str
        :param context: _description_
        :type context: str
        :return: _description_
        :rtype: Tuple[str, ReturnInfo]
        """
        answer, info = None, ReturnInfo()
        detected_lang = detect_lang(query) if self.config.lang == 'auto' else self.config.lang
        self.log(f"DETECTED LANG: {detected_lang}", verbose=self.config.verbose)

        formated_input = self.config.user_prompt[detected_lang].format(q=query, c=context)

        raw_output = self.agent.generate(
            system_prompt=self.config.system_prompt[detected_lang],
            user_prompt=formated_input).strip()
        self.log(f"RAW_ANSWER: {raw_output}", verbose=self.config.verbose)

        answer, status = self.config.answer_parse_func[detected_lang](raw_output)
        self.log(f"PARSED_ANSWER: {answer}", verbose=self.config.verbose)
        if status == ReturnStatus.bad_format:
            self.log(QA_BAD_QA_PROMPT, verbose=self.config.verbose)

        if len(answer) == 0:
            info.status = ReturnStatus.empty_answer
            info.message = QA_EMPTY_ANSWER

        return answer, info
