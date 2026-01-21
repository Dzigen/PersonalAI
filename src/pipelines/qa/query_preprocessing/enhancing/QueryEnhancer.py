from dataclasses import dataclass, field
from typing import Tuple, List, Union, Dict
from copy import deepcopy

from .config import QE_MAIN_LOG_PATH
from .utils import QueryEnhancerTaskSolvers, QueryEnhancerAgentTasksConfig
from .....utils import accumulate_stage_info, CompositeModuleDetailedResult, ModuleType
from .....utils.cache_kv import CacheUtils
from .....utils.errors import STATUS_MESSAGE
from .....utils.data_structs import create_id, QueryPreprocessingInfo, BaseComponentConfig, LanguageConfig
from .....agents.utils import AbstractAgentConnector
from .....utils import ReturnInfo, Logger, ReturnStatus, AgentTaskSolver
from .....db_drivers.kv_driver import KeyValueDriverConfig
from .....utils.agent_stat_analyzer import AgentStatAnalyzerConfig
from .....utils.cache_kv.CacheOperations import CacheOperations
from .....utils.agent_stat_analyzer.AgentStatOperations import AgentStatOperations


@dataclass
class QueryEnhancerConfig(BaseComponentConfig, LanguageConfig):
    """Конфигурация QueryEnhancer-операции.

    :param agent_gen_stategy: Стратегия генерации текста для используемого LLM-агента. В случае None-значения будет использоваться стратегия по умолчанию. Значение по умолчанию None.
    :type agent_gen_stategy: Union[None,Dict[str, Union[str, int, float]]], optional
    :param agent_tasks_config: Конфигурации LLM-промптов для решения заданных задач с помощью LLM-агента. Значение по умолчанию QueryEnhancerAgentTasksConfig().
    :type agent_tasks_config: Union[Dict,QueryEnhancerAgentTasksConfig], optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы QueryEnhancer-класса. Значение по умолчанию 'qp_enhancing_stage_cache'.
    :type cache_table_name: str, optional
    """
    agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]] = None
    agent_tasks_config: Union[Dict, QueryEnhancerAgentTasksConfig] = field(default_factory=lambda: QueryEnhancerAgentTasksConfig())

    cache_table_name: str = 'qp_enhancing_stage_cache'
    log: Logger = field(default_factory=lambda: Logger(QE_MAIN_LOG_PATH))

    def to_str(self):
        return f"{self.lang}|{self.agent_gen_stategy}|{self.agent_tasks_config.to_str()}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = QueryEnhancerConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.agent_tasks_config, dict):
            self.agent_tasks_config = QueryEnhancerAgentTasksConfig.from_dict(self.agent_tasks_config)


class QueryEnhancer(CacheUtils, CacheOperations, AgentStatOperations):
    """Класс, реализующий одну из операций по форматированию/предобработке user-вопроса в рамках QueryPreprocessor-стадии. Данный класс выполняет добавление дополнительных языковых конструкций в user-вопрос, с целью упрощения процесса по распознаванию заложенного запроса/интента.

    :param agent: Коннектор к конкретному LLM-агенту для выполнения inference-операций.
    :type agent: AbstractAgentConnector
    :param config: Конфигурация QueryEnhancer-операции. Значение по умолчанию QueryEnhancerConfig().
    :type config: Union[Dict,QueryEnhancerConfig], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: KeyValueDriverConfig, optional
    :param cache_llm_inference: Если True, то все результаты решения атомарных LLM-задач будут кешироваться, иначе False. Значение по умолчанию True.
    :type cache_llm_inference: bool, optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операций в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    """

    def __init__(self, agent: AbstractAgentConnector, config: Union[Dict, QueryEnhancerConfig] = QueryEnhancerConfig(),
                 cache_kvdriver_config: KeyValueDriverConfig = None,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None,
                 cache_llm_inference: bool = True):
        if isinstance(config, dict):
            config: QueryEnhancerConfig = QueryEnhancerConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config = config
        self.config.agent_tasks_config.versions_to_configs()

        self.cachekv = self.init_cachekv(cache_kvdriver_config, config.cache_table_name)

        self.agent = agent
        agents_cache_config = None
        if cache_llm_inference:
            agents_cache_config = cache_kvdriver_config if cache_llm_inference else None

        self.tasks_solvers: QueryEnhancerTaskSolvers = QueryEnhancerTaskSolvers(
            # добавление более понятных языковых конструкций
            queryexpansion_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.qexpan, agents_cache_config, inferencestat_config
            ),
            # добавление терминологии
            termscheck_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.termscheck, agents_cache_config, inferencestat_config
            ),
            # лингвистическая корректировка
            linguistcheck_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.lingcheck, agents_cache_config, inferencestat_config
            )
        )

        self.log = self.config.log
        self.verbose = self.config.verbose

    def get_cache_key(self, query_info: QueryPreprocessingInfo) -> List[str]:
        """Формирует ключ кеша для результата операции обогащения.
        В ключ включаются строковое представление входной структуры QueryPreprocessingInfo, строковое представление конфигурации и идентификатор используемого LLM-агента.

        :param query_info: Класс с информацией о предобработанном запросе.
        :type query_info: QueryPreprocessingInfo
        :return: Список строк, используемый как составной ключ кеша.
        :rtype: List[str]
        """
        str_using_agent_info = f"{self.agent.CONNECTOR_KW}:{self.agent.config.to_str()}"
        return [query_info.to_str(), self.config.to_str(), str_using_agent_info]

    @accumulate_stage_info
    @CacheUtils.cache_method_output
    def perform(self, query_info: QueryPreprocessingInfo) -> Tuple[str, ReturnInfo, CompositeModuleDetailedResult]:
        """Метод предназначен для выполнения операции форматирования/предобработки user-вопроса: переформулирование user-вопроса для выделения запроса/интента.

        :param query_info: Структура данных с результатами предыдущих операций предобратки/форматирования исходного user-вопроса.
        :type query_info: QueryPreprocessingInfo
        :return: Кортеж из трёх объектов: (1) модифицированный user-вопрос с добавленными языковыми конструкциями для выделения запроса/интента; (2) статус завершения операции с пояснительной информацией; (3) структура данных с промежуточными результатами реботы метода.
        :rtype: Tuple[str, ReturnInfo, CompositeModuleDetailedResult]
        """
        self.log("START QUERY ENHANCING...", verbose=self.verbose)
        self.log(f"BASE_QUESTION ID: {create_id(query_info.base_query)}", verbose=self.verbose)
        self.log(f"QUERY INFO: {query_info}", verbose=self.verbose)
        enhanced_query, rinfo = None, ReturnInfo()
        module_trace = CompositeModuleDetailedResult()

        if query_info.denoised_query is not None:
            query = query_info.denoised_query
        elif query_info.base_query is not None:
            query = query_info.base_query
        else:
            raise ValueError

        self.log("Добавление более понятных языковых конструкций в запрос с помощью LLM-агента...", verbose=self.verbose)
        expanded_query, status, trace = self.tasks_solvers.queryexpansion_solver.solve(
            lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, query=query)
        module_trace.add("queryexpansion_solver", ModuleType.task_solver, trace)
        if status != ReturnStatus.success:
            rinfo.occurred_warning.append(status)
        else:
            self.log(f"RESULT: {expanded_query}", verbose=self.verbose)

        if status == ReturnStatus.success:
            self.log("Замена слабоопределённых фраз в запросе на конкретную терминологию с помощью LLM-агента...", verbose=self.verbose)
            defined_query, status, trace = self.tasks_solvers.termscheck_solver.solve(
                lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, query=expanded_query)
            module_trace.add("termscheck_solver", ModuleType.task_solver, trace)
            if status != ReturnStatus.success:
                rinfo.occurred_warning.append(status)
            else:
                self.log(f"RESULT: {defined_query}", verbose=self.verbose)

        if status == ReturnStatus.success:
            self.log("Перефразирование запроса с соблюдением грамматики и синтаксиса используемого естественного языке с помощью LLM-агента...", verbose=self.verbose)
            reformulated_query, status, trace = self.tasks_solvers.linguistcheck_solver.solve(
                lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, query=defined_query)
            module_trace.add("linguistcheck_solver", ModuleType.task_solver, trace)
            if status != ReturnStatus.success:
                rinfo.occurred_warning.append(status)
            else:
                self.log(f"RESULT: {reformulated_query}", verbose=self.verbose)
                enhanced_query = reformulated_query

        if enhanced_query is None:
            rinfo.status = ReturnStatus.empty_answer
            rinfo.message = STATUS_MESSAGE[rinfo.status]

        self.log(f"RESULT: {enhanced_query}", verbose=self.verbose)
        self.log(f"STATUS: {rinfo.status}", verbose=self.verbose)

        return enhanced_query, rinfo, module_trace
