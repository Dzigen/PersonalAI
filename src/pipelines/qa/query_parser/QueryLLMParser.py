from dataclasses import dataclass, field
from typing import Tuple

from .configs import DEFAULT_KW_EXTRACTION_TASK_CONFIG, QP_MAIN_LOG_PATH
from ....utils.data_structs import QueryInfo, create_id
from ....utils.errors import STATUS_MESSAGE
from ....utils import Logger, ReturnStatus, ReturnInfo, AgentTaskSolver, AgentTaskSolverConfig
from ....agents import AgentDriver, AgentDriverConfig

@dataclass
class QueryLLMParserConfig:
    """Конфигурация "Query Parser"-стадии QA-конвейера.

    :param lang: Язык, который будет использоваться в подаваемом на вход тексте. На основании выбранного языка будут использоваться соответствующие промпты при инференсе LLM-агента. Если 'auto', то язык определяется автоматически. Значение по умолчанию 'auto'.
    :type lang: str
    :param agent_cofig: Конфигурация LLM-агента, который будет использоваться в рамках данной стадии. Значение по умолчанию AgentDriverConfig().
    :type agent_cofig: AgentDriverConfig
    :param kw_extraction_task_config: Конфигурация атомарной задачи для LLM-агента по извлечению кючевых сущностей из текста.
    :type kw_extraction_task_config: AgentTaskSolverConfig
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой комопненты. Значение по умолчанию Logger(QP_LOG_PATH).
    :type log: Logger
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool
    """
    lang: str = 'auto'
    agent_cofig: AgentDriverConfig = field(default_factory=lambda: AgentDriverConfig())
    kw_extraction_task_config: AgentTaskSolverConfig = field(default_factory=lambda: DEFAULT_KW_EXTRACTION_TASK_CONFIG)

    log: Logger = field(default_factory=lambda: Logger(QP_MAIN_LOG_PATH))
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

        info = ReturnInfo()
        self.log("START KEY WORD EXTRACTION...", verbose=self.config.verbose)
        self.log(f"BASE_QUESTION ID: {create_id(query)}", verbose=self.config.verbose)
        self.log(f"BASE_QUESTION: {query}", verbose=self.config.verbose)

        self.log("Выполнение извлечения ключевых сущностей из запроса с помощью LLM-агента...", verbose=self.config.verbose)
        extracted_entities, status = self.kw_extraction_solver.solve(lang=self.config.lang, query=query)

        if status != ReturnStatus.success:
            info.occurred_warning.append(status)

        if extracted_entities is None or len(extracted_entities) == 0:
            info.status = ReturnStatus.zero_entities
            info.message = STATUS_MESSAGE[info.status]

        query_struct = QueryInfo(query=query, entities=extracted_entities)

        self.log(f"RESULT: {len(extracted_entities)}", verbose=self.config.verbose)
        for entity in extracted_entities:
            self.log(f"* {entity}", verbose=self.config.verbose)
        self.log(f"STATUS: {STATUS_MESSAGE[info.status]}", verbose=self.config.verbose)

        return query_struct, info
