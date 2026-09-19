from dataclasses import dataclass, field
from typing import Union, Tuple, List, Dict
from copy import deepcopy

from .configs import QP_MAIN_LOG_PATH
from .utils import WeakQueryParserTaskSolvers, QueryLLMParserAgentTasksConfig
from ......utils.data_structs import QueryInfo, create_id, BaseComponentConfig, LanguageConfig
from ......utils.errors import STATUS_MESSAGE
from ......utils import Logger, ReturnStatus, ReturnInfo, AgentTaskSolver, accumulate_stage_info, \
    CompositeModuleDetailedResult, ModuleType
from ......agents.utils import AbstractAgentConnector
from ......utils.cache_kv import CacheUtils
from ......db_drivers.kv_driver import KeyValueDriverConfig
from ......utils.cache_kv.CacheOperations import CacheOperations
from ......utils.agent_stat_analyzer.AgentStatOperations import AgentStatOperations
from ......utils.agent_stat_analyzer import AgentStatAnalyzerConfig


@dataclass
class QueryLLMParserConfig(BaseComponentConfig, LanguageConfig):
    """Конфигурация "Query Parser"-стадии QA-конвейера.

    :param agent_gen_stategy: Стратегия генерации текста для используемого LLM-агента. В случае None-значения будет использоваться стратегия по умолчанию. Значение по умолчанию None.
    :type agent_gen_stategy: Union[None,Dict[str, Union[str, int, float]]], optional
    :param agent_tasks_config: Конфигурации LLM-промптов для решения заданных задач с помощью LLM-агента. Значение по умолчанию QueryLLMParserAgentTasksConfig().
    :type agent_tasks_config: Union[QueryLLMParserAgentTasksConfig,Dict], optional
    :param max_entities: Максимальное количество сущностей, которое может быть извлечено из заданного текста на естественном языке. Значение по умолчанию 20.
    :type max_entities: int, optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы QueryLLMParser-класса. Значение по умолчанию 'qa_queryparser_stage_cache'.
    :type cache_table_name: str, optional
    """
    agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]] = None
    agent_tasks_config: Union[QueryLLMParserAgentTasksConfig, Dict] = field(default_factory=lambda: QueryLLMParserAgentTasksConfig())
    max_entities: int = 20

    cache_table_name: str = 'qa_queryparser_stage_cache'
    log_path: str = QP_MAIN_LOG_PATH

    def to_str(self):
        return f"{self.agent_gen_stategy}|{self.agent_tasks_config.to_str()}|{self.max_entities}|{self.lang}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = QueryLLMParserConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.agent_tasks_config, dict):
            self.agent_tasks_config = QueryLLMParserAgentTasksConfig.from_dict(self.agent_tasks_config)


class QueryLLMParser(CacheUtils, CacheOperations, AgentStatOperations):
    """Верхнеуровневый класс первой стадии QA-конвейера для извлечения сущностей из запроса на естественном языке.

    :param agent: Коннектор к конкретному LLM-агенту для выполнения inference-операций.
    :type agent: AbstractAgentConnector
    :param config: Конфигурация "Query Parser"-стадии. Значение по умолчанию QueryLLMParserConfig().
    :type config: Union[QueryLLMParserConfig,Dict], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операций в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    :param cache_llm_inference: Если True, то все результаты решения атомарных LLM-задач будут кешироваться, иначе False. Значение по умолчанию True.
    :type cache_llm_inference: bool, optional
    """

    def __init__(self, agent: AbstractAgentConnector, config: Union[QueryLLMParserConfig, Dict] = QueryLLMParserConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None,
                 cache_llm_inference: bool = True) -> None:
        if isinstance(config, dict):
            config: QueryLLMParserConfig = QueryLLMParserConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config = config
        self.config.agent_tasks_config.versions_to_configs(self.config.verbose, self.config.log_level)

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, config.cache_table_name)

        self.agent = agent
        kwe_task_cache_config = None
        if cache_llm_inference:
            kwe_task_cache_config = deepcopy(cache_kvdriver_config)

        self.tasks_solvers: WeakQueryParserTaskSolvers = WeakQueryParserTaskSolvers(
            kw_extraction_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.kw_extraction,
                kwe_task_cache_config, inferencestat_config)
        )

        self.log = Logger(config.log_path)
        self.verbose = config.verbose
        self.log_level = config.log_level

    def get_cache_key(self, query_info: QueryInfo) -> List[object]:
        """Формирует составной ключ кэша для результатов извлечения сущностей.

        В ключ включается строковое представление конфигурации парсера запросов, идентификатор и конфигурация используемого LLM-агента, сериализованное представление входного QueryInfo.

        :param query_info: Структура с исходным запросом и производными полями.
        :type query_info: QueryInfo
        :return: Список строк, используемый как составной ключ кеша.
        :rtype: List[object]
        """
        str_using_agent_info = f"{self.agent.CONNECTOR_KW}:{self.agent.config.to_str()}"
        return [self.config.to_str(), str_using_agent_info, query_info.to_str()]

    @accumulate_stage_info
    @CacheUtils.cache_method_output
    def extract_entities(self, query_info: QueryInfo) -> Tuple[List[str], ReturnInfo, CompositeModuleDetailedResult]:
        """Метод предназначен для извлечения ключевых сущностей из query-текста.

        :param query_info: Структура данных с информацией об обрабатываемом запросе.
        :type query_info: QueryInfo
        :return: Кортеж из трёх объектов: (1) структура данных со списком извлечённых ключевых сущностей из query; (2) статус завершения операции с пояснительной информацией; (3) структура данных с промежуточными результатами реботы метода.
        :rtype: Tuple[List[str], ReturnInfo, CompositeModuleDetailedResult]
        """
        self.log.debug("START KEY WORD EXTRACTION...", verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Question hash: %s", create_id(query_info.query), verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Question: %s", query_info.query, verbose=self.verbose, log_level=self.log_level)
        rinfo, module_trace = ReturnInfo(), CompositeModuleDetailedResult()

        self.log.debug("Выполнение извлечения ключевых сущностей из запроса с помощью LLM-агента...", verbose=self.verbose, log_level=self.log_level)
        extracted_entities, status, trace = self.tasks_solvers.kw_extraction_solver.solve(
            lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, query=query_info.query)
        module_trace.add("kw_extraction_solver", ModuleType.task_solver, trace)
        if status != ReturnStatus.success:
            rinfo.occurred_warning.append(status)

        entities = []
        if extracted_entities is None or len(extracted_entities) == 0:
            rinfo.status = ReturnStatus.zero_entities
            rinfo.message = STATUS_MESSAGE[rinfo.status]
        else:
            self.log.debug("Количество извлечённых сущностей, до урезания: %d", len(extracted_entities), verbose=self.verbose, log_level=self.log_level)
            self.log.debug("TMP_RESULT: %s", extracted_entities, verbose=self.verbose, log_level=self.log_level)
            entities = extracted_entities[:self.config.max_entities]
            self.log.debug("RESULT: %d", len(entities), verbose=self.verbose, log_level=self.log_level)
            for entity in entities:
                self.log.debug("* %s", entity, verbose=self.verbose, log_level=self.log_level)

        self.log.debug("STATUS: %s", STATUS_MESSAGE[rinfo.status], verbose=self.verbose, log_level=self.log_level)

        return entities, rinfo, module_trace
