from typing import List
from dataclasses import dataclass, field\

from .utils import QA_USER_PROMPT, QA_SYSTEM_PROMPT, QA_LOG_PATH
from ...utils.data_structs import Triplet
from ...agents import AgentDriver, AgentDriverConfig
from ...utils.data_structs import TripletCreator
from ...utils.data_structs import RelationType
from ...utils import Logger, detect_lang

@dataclass
class QALLMGeneratorConfig:
    lang: str = "auto"
    system_prompt: dict = field(default_factory=lambda: QA_SYSTEM_PROMPT)
    user_prompt: dict = field(default_factory=lambda: QA_USER_PROMPT)
    agent_cofig: AgentDriverConfig = field(default_factory=lambda: AgentDriverConfig())
    relation_type: List[RelationType] = field(default_factory=lambda: [RelationType.simple, RelationType.hyper, RelationType.episodic])
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

    def generate(self, query: str, context: str) -> str:
        """_summary_

        :param query: _description_
        :type query: str
        :param context: _description_
        :type context: str
        :return: _description_
        :rtype: str
        """
        detected_lang = detect_lang(query) if self.config.lang == 'auto' else self.config.lang
        self.log(f"DETECTED LANG: {detected_lang}", verbose=self.config.verbose)

        formated_input = self.config.user_prompt[detected_lang].format(q=query, c=context)

        found_line = ""
        raw_output = self.agent.generate(
            system_prompt=self.config.system_prompt[detected_lang],
            user_prompt=formated_input).strip()
        self.log(f"RAW_ANSWER: {raw_output}", verbose=self.config.verbose)

        # TO MODIFY
        if detected_lang == "en":
            for line in raw_output.split("\n"):
                if "Final answer 3" in line:
                    found_line = line
                    break
            if found_line:
                self.log("FORMATED ANSWER", verbose=self.config.verbose)
                answer = found_line.split("Final answer 3: ")[-1]
            else:
                self.log("NOT FORMATED ANSWER", verbose=self.config.verbose)
                answer = raw_output
        elif detected_lang == "ru":
            answer = raw_output

        return answer
