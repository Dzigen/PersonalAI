from dataclasses import dataclass, field
from typing import Tuple

from .configs import DEFAULT_KW_EXTRACTION_TASK_CONFIG, QP_LOG
from ....utils.data_structs import QueryInfo
from ....utils.errors import QA_ZERO_ENTITIES_MSG
from ....utils import Logger, detect_lang, ReturnStatus, ReturnInfo, AgentTaskSolver, AgentTaskSolverConfig
from ....agents import AgentDriver, AgentDriverConfig

@dataclass
class QueryLLMParserConfig:
    """Конфигурация "Query Parser"-стадии.

    :param lang: Язык, который будет использоваться в подаваемом на вход тексте. На основании выбранного языка будут использоваться соответствующие промпты. Если 'auto', то язык определяется автоматически. Значение по умолчанию 'auto'.
    :type lang: str
    :param ents_extr_config: Конфигурация алгоритма по извлечению ключевых сущностей из текста. Значение по умолчанию EntitiesExtractorConfig().
    :type ents_extr_config: EntitiesExtractorConfig
    :param agent_cofig: Конфигурация LLM-агента, который будет использоваться в рамках данной стадии. Значение по умолчанию AgentDriverConfig().
    :type agent_cofig: AgentDriverConfig
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой комопненты. Значение по умолчанию Logger(QP_LOG_PATH).
    :type log: Logger
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool
    """
    lang: str = 'auto'
    kw_extraction_task_config: AgentTaskSolverConfig = field(default_factory=lambda: DEFAULT_KW_EXTRACTION_TASK_CONFIG)
    agent_cofig: AgentDriverConfig = field(default_factory=lambda: AgentDriverConfig())
    log: Logger = field(default_factory=lambda: Logger(QP_LOG))
    verbose: bool = False

class QueryLLMParser:
    """Верхнеуровневый класс первой стадии QA-конвейера
    для извлечения сущностей из user-вопроса.

    :param config: Конфигурация "Query Parser"-стадии. Значение по умолчанию QueryLLMParserConfig().
    :type config: QueryLLMParserConfig
    """
    def __init__(self, config: QueryLLMParserConfig = QueryLLMParserConfig()) -> None:
        self.config = config
        self.log = self.config.log

        self.agent = AgentDriver.connect(config.agent_cofig)
        self.kw_extraction_solver = AgentTaskSolver(self.agent, self.config.kw_extraction_task_config)

    def extract_entities(self, query: str) -> Tuple[QueryInfo, ReturnInfo]:
        """Метод предназначен для извлечения ключевых сущностей из query-текста.

        :param query: Текст на естественном языке.
        :type query: str
        :return: Кортеж из двух объектов: (1) структура данных со списком извлечённых ключевых сущностей из query; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[QueryInfo, ReturnInfo]
        """
        extracted_entities, info = self.kw_extraction_solver.solve(
            lang=self.config.lang, query=query)

        if len(extracted_entities) == 0:
            info.status = ReturnStatus.zero_entities
            info.message = QA_ZERO_ENTITIES_MSG

        return QueryInfo(query=query, entities=extracted_entities), info
