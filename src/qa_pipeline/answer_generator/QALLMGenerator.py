from .utils import QUESTION_ANSWERING_USER_PROMPT, RelationType
from ...utils.data_structs import Triplet
from ...llm_agent import AgentConnector
from ...embedding_functions import EmbeddingsDatabaseConnection

from typing import List
from dataclasses import dataclass, field


@dataclass
class QALLMGeneratorConfig:
    user_prompt: str = QUESTION_ANSWERING_USER_PROMPT
    relation_type: List[RelationType] = field(default_factory=lambda: 
                                            [RelationType.simple, RelationType.hyper, RelationType.episodic])

class QALLMGenerator:
    """Главный класс для генерации ответов по пользовательским вопросам на основе 
    извлечённой информации из графа знаний
    """
    def __init__(self, llm_agent: AgentConnector, config: QALLMGeneratorConfig = QALLMGeneratorConfig()) -> None:
        self.llm_agent = llm_agent
        self.config = config

    def formate_context(self, triplets: List[Triplet]) -> str:
        filtered_context = list(map(lambda triplet: EmbeddingsDatabaseConnection.formate_triplete(triplet), triplets))
        filtered_context = list(map(lambda triplet: triplet[1], filtered_context))                
        return "\n".join(filtered_context)

    def generate(self, query: str, context: str) -> str:
        formated_input = self.config.user_prompt.format(q=query, c=context)

        found_line = ""
        raw_output = self.llm_agent.generate(formated_input).strip()
        for line in raw_output.split("\n"):
            if "Final answer 3" in line:
                found_line = line
                break
        if found_line:
            answer = found_line.split("Final answer 3: ")[-1]
        else:
            answer = raw_output.split("\n")[1]

        return answer