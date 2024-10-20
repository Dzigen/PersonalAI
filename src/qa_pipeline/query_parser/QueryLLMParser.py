from dataclasses import dataclass, field

from .utils import EntitiesExtractorConfig, QP_LOG_PATH
from ...utils.data_structs import QueryInfo
from ...utils import Logger
from ...agents import AgentDriver, AgentDriverConfig

@dataclass
class QueryLLMParserConfig:
    lang: str = 'en'
    ents_extr_config: EntitiesExtractorConfig = field(default_factory=lambda: EntitiesExtractorConfig()) 
    agent_cofig: AgentDriverConfig = field(default_factory=lambda: AgentDriverConfig())
    log: Logger = field(default_factory=lambda: Logger(QP_LOG_PATH))
    verbose: bool = False

class QueryLLMParser:
    """Главный класс для извлечения полезной информации 
    из пользовательского запроса
    """
    def __init__(self, config: QueryLLMParserConfig = QueryLLMParserConfig()) -> None:
        self.config = config
        
        self.agent = AgentDriver.connect(config.agent_cofig)
        self.log = self.config.log

    def extract_entities(self, query: str) -> QueryInfo:
        formated_input = self.config.ents_extr_config.user_prompt[self.config.lang].format(text=query)
        raw_output = self.agent.generate(
            system_prompt=self.config.ents_extr_config.system_prompt[self.config.lang], 
            user_prompt=formated_input)
        self.log(f"RAW_ENTITIES: {raw_output}", verbose=self.config.verbose)

        extracted_entities = list(filter(lambda item: len(item) > 0, list(map(lambda item: item.strip(), raw_output.split('|')))))

        return QueryInfo(query=query, entities=extracted_entities)