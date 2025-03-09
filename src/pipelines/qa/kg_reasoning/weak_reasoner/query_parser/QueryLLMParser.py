from dataclasses import dataclass, field
from typing import Union, Tuple, List

from .configs import DEFAULT_KWE_TASK_CONFIG, QP_MAIN_LOG_PATH
from ......utils.data_structs import QueryInfo, create_id
from ......utils.errors import STATUS_MESSAGE
from ......utils import Logger, ReturnStatus, ReturnInfo, AgentTaskSolver, AgentTaskSolverConfig
from ......agents import AgentDriver, AgentDriverConfig
from ......utils.cache_kv import CacheKV, CacheUtils
from ......db_drivers.kv_driver import KeyValueDriverConfig


@dataclass
class QueryLLMParserConfig:
    """Конфигурация "Query Parser"-стадии QA-конвейера.

    :param lang: Язык, который будет использоваться в подаваемом на вход тексте. На основании выбранного языка будут использоваться соответствующие промпты при инференсе LLM-агента. Если 'auto', то язык определяется автоматически. Значение по умолчанию 'auto'.
    :type lang: str
    :param adriver_config: Конфигурация LLM-агента, который будет использоваться в рамках данной стадии. Значение по умолчанию AgentDriverConfig().
    :type adriver_config: AgentDriverConfig
    :param kw_extraction_task_config: Конфигурация атомарной задачи для LLM-агента по извлечению ключевых сущностей из текста. Значение по умолчанию DEFAULT_KWE_TASK_CONFIG.
    :type kw_extraction_task_config: AgentTaskSolverConfig
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой комопненты. Значение по умолчанию Logger(QP_LOG_PATH).
    :type log: Logger
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool
    """
    lang: str = 'auto'
    adriver_config: AgentDriverConfig = field(default_factory=lambda: AgentDriverConfig())
    kw_extraction_task_config: AgentTaskSolverConfig = field(default_factory=lambda: DEFAULT_KWE_TASK_CONFIG)
    cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None

    log: Logger = field(default_factory=lambda: Logger(QP_MAIN_LOG_PATH))
    verbose: bool = False

class QueryLLMParser(CacheUtils):
    """Верхнеуровневый класс первой стадии QA-конвейера
    для извлечения сущностей из user-вопроса.

    :param config: Конфигурация "Query Parser"-стадии. Значение по умолчанию QueryLLMParserConfig().
    :type config: QueryLLMParserConfig
    """
    def __init__(self, config: QueryLLMParserConfig = QueryLLMParserConfig()) -> None:
        self.config = config
        self.log = self.config.log

        self.agent = AgentDriver.connect(config.adriver_config)
        self.kw_extraction_solver = AgentTaskSolver(self.agent, self.config.kw_extraction_task_config)

        if self.config.cache_kvdriver_config is not None:
            self.cachekv = CacheKV(self.config.cache_kvdriver_config)
        else:
            self.cachekv = None

    def get_cache_key(self, query: str) -> List[object]:
        return [self.config.lang, self.config.adriver_config,
                self.config.kw_extraction_task_config, query]

    @CacheUtils.cache_method_output
    def extract_entities(self, query: str) -> Tuple[List[str], ReturnInfo]:
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

        entities=[]
        if extracted_entities is None or len(extracted_entities) == 0:
            info.status = ReturnStatus.zero_entities
            info.message = STATUS_MESSAGE[info.status]
        else:
            entities=extracted_entities

        self.log(f"RESULT: {len(entities)}", verbose=self.config.verbose)
        for entity in entities:
            self.log(f"* {entity}", verbose=self.config.verbose)
        self.log(f"STATUS: {STATUS_MESSAGE[info.status]}", verbose=self.config.verbose)

        return entities, info
