from ...agents.llama_agent import LLaMAagent
from .utils import QALLMGeneratorConfig
from ..knowledge_retriever.utils import Triplet

from typing import List

class QALLMGenerator:

    def __init__(self, llm_agent: LLaMAagent, config: QALLMGeneratorConfig) -> None:
        self.llm_agent = llm_agent
        self.config = config

    def formate_context(self, triplets: List[Triplet]) -> str:
        # TODO
        pass

    def generate_answer(self, query: str, context: str) -> str:
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