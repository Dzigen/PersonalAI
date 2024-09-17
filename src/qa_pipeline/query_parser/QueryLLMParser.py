from dataclasses import dataclass

from .utils import EntitiesExtractorConfig
from ...utils.data_structs import QueryInfo
from ...agents.llama_agent import LLaMAagent

@dataclass
class QueryLLMParserConfig:
    ents_extr_config: EntitiesExtractorConfig


class QueryLLMParser:
    """Главный класс для извлечения полезной информации 
    из пользовательского запроса
    """
    def __init__(self, config: QueryLLMParserConfig, llm_agent: LLaMAagent) -> None:
        self.config = config
        self.llm_agent = llm_agent

    def extract_entities(self, query: str) -> QueryInfo:
        formated_input = self.config.ents_extr_config.user_prompt.format(text=query)
        raw_output = self.llm_agent.generate(formated_input)
        extracted_entities = list(filter(lambda item: len(item) > 0, list(map(lambda item: item.strip(), raw_output.split('|')))))

        return QueryInfo(query=query, entities=extracted_entities)