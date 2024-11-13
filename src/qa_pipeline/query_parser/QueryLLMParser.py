from dataclasses import dataclass, field
from typing import Tuple

from .utils import EntitiesExtractorConfig, QP_LOG_PATH
from ...utils.data_structs import QueryInfo
from ...utils import Logger, detect_lang, ReturnStatus, ReturnInfo
from ...utils.errors import QA_ZERO_ENTITIES_MSG, QA_BAD_ENTITIES_EXTRACTION_PROMPT_MSG, NOT_SUPPORTED_LANG_MSG
from ...agents import AgentDriver, AgentDriverConfig

@dataclass
class QueryLLMParserConfig:
    #: Язык, который будет использоваться в подаваемом на вход тексте. На основании выбранного языка будут использоваться соответствующие промпты. Если 'auto', то язык определяется автоматически.
    lang: str = 'auto'
    #: Конфигурация алгоритма по извлечению ключевых сущностей из текста.
    ents_extr_config: EntitiesExtractorConfig = field(default_factory=lambda: EntitiesExtractorConfig())
    #: Конфигурация LLM-агента, который будет использоваться в рамках данной стадии
    agent_cofig: AgentDriverConfig = field(default_factory=lambda: AgentDriverConfig())
    #
    log: Logger = field(default_factory=lambda: Logger(QP_LOG_PATH))
    verbose: bool = False

class QueryLLMParser:
    """Верхнеуровневый класс первой стадии QA-конвейера
    для извлечения сущностей из user-вопроса.
    """
    def __init__(self, config: QueryLLMParserConfig = QueryLLMParserConfig()) -> None:
        self.config = config

        self.agent = AgentDriver.connect(config.agent_cofig)
        self.log = self.config.log

    def extract_entities(self, query: str) -> Tuple[QueryInfo, ReturnInfo]:
        """Метод предназначен для извлечения ключевых сущностей из query-текста.

        :param query: Текст на естественном языке.
        :type query: str
        :return: Кортеж из двух объектов: (1) структура данных со списком извлечённых ключевых сущностей из query; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[QueryInfo, ReturnInfo]
        """
        extracted_entities, info = [], ReturnInfo()
        detected_lang, status = detect_lang(query) if self.config.lang == 'auto' else (self.config.lang, ReturnStatus.success)
        self.log(f"DETECTED LANG: {detected_lang}", verbose=self.config.verbose)
        if status == ReturnStatus.not_supported_lang:
            self.log(NOT_SUPPORTED_LANG_MSG, verbose=self.config.verbose)
            info.occurred_warning.append(status)

        if status == ReturnStatus.success:
            formated_input = self.config.ents_extr_config.user_prompt[detected_lang].format(text=query)
            raw_output = self.agent.generate(
                system_prompt=self.config.ents_extr_config.system_prompt[detected_lang],
                user_prompt=formated_input)
            self.log(f"RAW_ENTITIES: {raw_output}", verbose=self.config.verbose)

            extracted_entities, status = self.config.ents_extr_config.entities_parse_func[detected_lang](raw_output)
            self.log(f"PARSED_ENTITIES: {extracted_entities}", verbose=self.config.verbose)
            if status == ReturnStatus.bad_format:
                self.log(QA_BAD_ENTITIES_EXTRACTION_PROMPT_MSG, verbose=self.config.verbose)
                info.occurred_warning.append(status)

        if len(extracted_entities) == 0:
            info.status = ReturnStatus.zero_entities
            info.message = QA_ZERO_ENTITIES_MSG

        return QueryInfo(query=query, entities=extracted_entities), info
