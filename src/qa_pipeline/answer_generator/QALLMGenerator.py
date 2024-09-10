from ...agents.llama_agent import LLaMAagent
from .utils import QALLMGeneratorConfig, ContextType
from ..knowledge_retriever.utils import Triplet

from typing import List

class QALLMGenerator:
    """Главный класс для генерации ответов по пользовательским вопросам на основе 
    извлечённой информации из графа знаний
    """
    def __init__(self, llm_agent: LLaMAagent, config: QALLMGeneratorConfig) -> None:
        self.llm_agent = llm_agent
        self.config = config
        self.stringi

    def formate_context(self, triplets: List[Triplet]) -> str:
        """_summary_

        Args:
            triplets (List[Triplet]): _description_

        Raises:
            KeyError: _description_

        Returns:
            str: _description_
        """
        filtered_context = []
        for triplet in triplets:
            rel_type = triplet.relation.type
            if rel_type in self.config.context_type:
                if (rel_type == ContextType.episodic) or (rel_type == ContextType.hyper):
                    filtered_context.append(
                        triplet.relation.prop["time"] + ": " + triplet.end_node.name)
                elif rel_type == ContextType.simple:
                    filtered_context.append(
                        triplet.relation.prop["time"] + ": " + " ".join(
                            [triplet.start_node.name, triplet.relation.name, triplet.end_node.name]))
                else:
                    raise KeyError
                
        return "\n".join(filtered_context)

    def generate(self, query: str, context: str) -> str:
        """_summary_

        Args:
            query (str): _description_
            context (str): _description_

        Returns:
            str: _description_
        """
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