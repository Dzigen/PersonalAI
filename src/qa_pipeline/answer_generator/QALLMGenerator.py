from typing import List
from dataclasses import dataclass, field

from .utils import QA_USER_PROMPT, QA_SYSTEM_PROMPT, QA_LOG_PATH
from ...utils.data_structs import Triplet
from ...agents import AgentDriver, AgentDriverConfig
from ...utils.data_structs import TripletCreator
from ...utils.data_structs import RelationType
from ...utils import Logger

@dataclass
class QALLMGeneratorConfig:
    lang: str = "ru"
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
        self.config = config
        self.agent = AgentDriver.connect(config.agent_cofig)
        self.log = self.config.log

    def formate_context(self, triplets: List[Triplet]) -> str:
        filtered_context = list(map(lambda triplet: f"- {TripletCreator.stringify(triplet)[1] if triplet.stringified is None else triplet.stringified}", triplets))                
        return "\n".join(filtered_context)

    def generate(self, query: str, context: str) -> str:
        lang = self.config.lang
        formated_input = self.config.user_prompt[lang].format(q=query, c=context)

        found_line = ""
        raw_output = self.agent.generate(formated_input).strip()
        self.log(f"RAW_ANSWER: {raw_output}", verbose=self.config.verbose)

        # TO MODIFY
        if lang == "en":
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
        elif lang == "ru":
            answer = raw_output

        return answer