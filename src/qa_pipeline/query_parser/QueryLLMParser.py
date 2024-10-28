from dataclasses import dataclass, field
from typing import Tuple

from .utils import EntitiesExtractorConfig, QP_LOG_PATH
from ...utils.data_structs import QueryInfo
from ...utils import Logger, detect_lang, ReturnStatus
from ...utils.errors import QA_ZERO_ENTITIES_MSG
from ...agents import AgentDriver, AgentDriverConfig

@dataclass
class QueryLLMParserConfig:
    """_summary_
    """
    #
    lang: str = 'auto'
    #
    ents_extr_config: EntitiesExtractorConfig = field(default_factory=lambda: EntitiesExtractorConfig())
    #
    agent_cofig: AgentDriverConfig = field(default_factory=lambda: AgentDriverConfig())
    #
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

    def extract_entities(self, query: str) -> Tuple[QueryInfo, ReturnStatus, str]:
        """_summary_

        :param query: _description_
        :type query: str
        :return: _description_
        :rtype: QueryInfo
        """
        detected_lang = detect_lang(query) if self.config.lang == 'auto' else self.config.lang
        self.log(f"DETECTED LANG: {detected_lang}", verbose=self.config.verbose)

        formated_input = self.config.ents_extr_config.user_prompt[detected_lang].format(text=query)
        raw_output = self.agent.generate(
            system_prompt=self.config.ents_extr_config.system_prompt[detected_lang],
            user_prompt=formated_input)
        self.log(f"RAW_ENTITIES: {raw_output}", verbose=self.config.verbose)

        extracted_entities = self.config.ents_extr_config.entities_parse_func[detected_lang](raw_output)
        self.log(f"PARSED_ENTITIES: {extracted_entities}", verbose=self.config.verbose)

        status, msg = ReturnStatus.success, ""
        if len(extracted_entities) == 0:
            status, msg = ReturnStatus.warning, QA_ZERO_ENTITIES_MSG

        return QueryInfo(query=query, entities=extracted_entities), status, msg
