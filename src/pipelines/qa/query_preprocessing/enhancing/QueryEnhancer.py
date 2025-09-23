from dataclasses import dataclass, field
from typing import Tuple, List, Union, Dict

from .config import QE_MAIN_LOG_PATH, DEFAULT_QEXPAN_TASK_CONFIG, \
    DEFAULT_TCHECK_TASK_CONFIG, DEFAULT_LCHECK_TASK_CONFIG
from ..QueryPreprocessor import QueryPreprocessingInfo
from .....utils.cache_kv import CacheUtils
from .....utils.errors import STATUS_MESSAGE
from .....utils.data_structs import create_id
from .....agents.utils import AbstractAgentConnector
from .....utils import ReturnInfo, Logger, ReturnStatus, AgentTaskSolverConfig, AgentTaskSolver
from .....db_drivers.kv_driver import KeyValueDriverConfig


@dataclass
class QueryEnhancerConfig:
    """Конфигурация QueryEnhancer-операции.

    :param lang: Язык, который будет использоваться в подаваемом на вход тексте. На основании выбранного языка будут использоваться соответствующие промпты при инференсе LLM-агента. Если 'auto', то язык определяется автоматически. Значение по умолчанию 'auto'.
    :type lang: str, optional
    :param agent_gen_stategy: Стратегия генерации текста для используемого LLM-агента. В случае None-значение будет использоваться стратегия по умолчанию. Значение по умолчанию None.
    :type agent_gen_stategy: Union[None,Dict[str, Union[str, int, float]]], optional
    :param qexpan_agent_task_config: Конфигурация атомарной задачи для LLM-агента по добавлению более понятных языковых конструкций в запроc. Значение по умолчанию DEFAULT_QEXPAN_TASK_CONFIG.
    :type qexpan_agent_task_config: AgentTaskSolverConfig, optional
    :param termscheck_agent_task_config: Конфигурация атомарной задачи для LLM-агента по замене слабоопределённых фраз в запросе на конкретные термины. Значение по умолчанию DEFAULT_TCHECK_TASK_CONFIG.
    :type termscheck_agent_task_config: AgentTaskSolverConfig, optional
    :param lingcheck_agent_task_config: Конфигурация атомарной задачи для LLM-агента по перефразированию запроса с соблюдением грамматики и синтаксиса используемого естественного языке. Значение по умолчанию DEFAULT_LCHECK_TASK_CONFIG.
    :type lingcheck_agent_task_config: AgentTaskSolverConfig, optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы QueryEnhancer-класса. Значение по умолчанию 'qp_enhancing_stage_cache'.
    :type cache_table_name: str, optional
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты. Значение по умолчанию Logger(QE_MAIN_LOG_PATH).
    :type log: Logger, optional
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool, optional
    """
    lang: str = "auto"
    agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]] = None
    qexpan_agent_task_config: AgentTaskSolverConfig = field(
        default_factory=lambda: DEFAULT_QEXPAN_TASK_CONFIG)
    termscheck_agent_task_config: AgentTaskSolverConfig = field(
        default_factory=lambda: DEFAULT_TCHECK_TASK_CONFIG)
    lingcheck_agent_task_config: AgentTaskSolverConfig = field(
        default_factory=lambda: DEFAULT_LCHECK_TASK_CONFIG)

    cache_table_name: str = 'qp_enhancing_stage_cache'
    log: Logger = field(default_factory=lambda: Logger(QE_MAIN_LOG_PATH))
    verbose: bool = False

    def to_str(self):
        return f"{self.lang}|{self.agent_gen_stategy}|{self.qexpan_agent_task_config.version}|{self.termscheck_agent_task_config.version}|{self.lingcheck_agent_task_config.version}"


class QueryEnhancer(CacheUtils):
    """Класс, реализующий одну из операций по форматированию/предобработке user-вопроса в рамках QueryPreprocessor-стадии. Данный класс выполняет добавление дополнительных языковых конструкций в user-вопрос, с целью упрощения процесса по распознаванию заложенного запроса/интента.

    :param agent: Коннектор к конкретному LLM-агенту для выполнения inference-операций.
    :type agent: AbstractAgentConnector
    :param config: Конфигурация QueryEnhancer-операции. Значение по умолчанию QueryEnhancerConfig().
    :type config: QueryEnhancerConfig, optional
    :param cache_kvdriver_config:Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: KeyValueDriverConfig, optional
    :param cache_llm_inference: Если True, то все результаты решения атомарных LLM-задач будут кешироваться, иначе False. Значение по умолчанию True.
    :type cache_llm_inference: bool, optional
    """

    def __init__(self, agent: AbstractAgentConnector, config: QueryEnhancerConfig = QueryEnhancerConfig(),
                 cache_kvdriver_config: KeyValueDriverConfig = None, cache_llm_inference: bool = True):
        self.config = config
        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, config.cache_table_name)

        self.agent = agent
        agents_cache_config = None
        if cache_llm_inference:
            agents_cache_config = cache_kvdriver_config if cache_llm_inference else None

        # добавление более понятных языковых конструкций
        self.queryexpansion_solver = AgentTaskSolver(
            self.agent, self.config.qexpan_agent_task_config, agents_cache_config)
        # добавление терминологии
        self.termscheck_solver = AgentTaskSolver(
            self.agent, self.config.termscheck_agent_task_config, agents_cache_config)
        # лингвистическая корректировка
        self.linguistcheck_solver = AgentTaskSolver(
            self.agent, self.config.lingcheck_agent_task_config, agents_cache_config)

        self.log = self.config.log
        self.verbose = self.config.verbose

    def clear_kv_caches(self, level: str = 'all') -> None:
        # TODO
        pass

    def get_cache_key(self, query_info: QueryPreprocessingInfo) -> List[object]:
        return [query_info.to_str(), self.config.to_str()]

    @CacheUtils.cache_method_output
    def perform(self, query_info: QueryPreprocessingInfo) -> Tuple[str, ReturnInfo]:
        """Метод предназначен для выполнения операции форматирования/предобработки user-вопроса: переформилирование user-вопроса для выделения запроса/интента.

        :param query_info: Струкутра данных с результатами предыдущих операций предобратки/форматирования исходного user-вопроса.
        :type query_info: QueryPreprocessingInfo
        :return: Кортеж из двух объектов: (1) модифицированный user-вопрос с добавленными языковыми конструкциями для выделения запроса/интента; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[str, ReturnInfo]
        """
        self.log("START QUERY DENOISING...", verbose=self.config.verbose)
        self.log(
            f"BASE_QUESTION ID: {create_id(query_info.base_query)}", verbose=self.config.verbose)
        self.log(f"QUERY INFO: {query_info}", verbose=self.config.verbose)
        enhanced_query, rinfo = None, ReturnInfo()

        if query_info.denoised_query is not None:
            query = query_info.denoised_query
        elif query_info.base_query is not None:
            query = query_info.base_query
        else:
            raise ValueError

        self.log("Выполнение добавление более понятных языковых конструкций в запрос с помощью LLM-агента...",
                 verbose=self.config.verbose)
        expanded_query, status = self.queryexpansion_solver.solve(
            lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, query=query)
        if status != ReturnStatus.success:
            rinfo.occurred_warning.append(status)
        else:
            self.log(f"RESULT: {expanded_query}", verbose=self.config.verbose)

        if status == ReturnStatus.success:
            self.log("Выполнение замены слабоопределённых фраз в запросе на конкретную терминологии с помощью LLM-агента...",
                     verbose=self.config.verbose)
            defined_query, status = self.termscheck_solver.solve(
                lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy,
                query=expanded_query)
            if status != ReturnStatus.success:
                rinfo.occurred_warning.append(status)
            else:
                self.log(f"RESULT: {defined_query}",
                         verbose=self.config.verbose)

        if status == ReturnStatus.success:
            self.log("Выполнение перефразирования запроса с соблюдением грамматики и синтаксиса используемого естественного языке с помощью LLM-агента...", verbose=self.config.verbose)
            reformulated_query, status = self.linguistcheck_solver.solve(
                lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy,
                query=defined_query)
            if status != ReturnStatus.success:
                rinfo.occurred_warning.append(status)
            else:
                self.log(f"RESULT: {reformulated_query}",
                         verbose=self.config.verbose)
                enhanced_query = reformulated_query

        if enhanced_query is None:
            rinfo.status = ReturnStatus.empty_answer
            rinfo.message = STATUS_MESSAGE[rinfo.status]

        self.log(f"RESULT: {enhanced_query}", verbose=self.config.verbose)
        self.log(f"STATUS: {rinfo.status}", verbose=self.config.verbose)

        return enhanced_query, rinfo
