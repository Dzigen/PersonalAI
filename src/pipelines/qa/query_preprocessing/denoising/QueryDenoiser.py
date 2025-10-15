from dataclasses import dataclass, field
from typing import Tuple, List, Union, Dict

from .config import QD_MAIN_LOG_PATH, DEFAULT_SWREMV_TASK_CONFIG, DEFAULT_GRAMCHECK_TASK_CONFIG
from ..QueryPreprocessor import QueryPreprocessingInfo
from .....utils.cache_kv import CacheUtils
from .....utils.errors import STATUS_MESSAGE
from .....utils.data_structs import create_id
from .....agents.utils import AbstractAgentConnector
from .....utils import ReturnInfo, Logger, ReturnStatus, AgentTaskSolverConfig, AgentTaskSolver
from .....db_drivers.kv_driver import KeyValueDriverConfig
from .....utils.cache_kv.utils import AbstractCacheInfo
from .....utils.agent_stat_analyzer import AgentStatAnalyzerConfig


@dataclass
class QueryDenoiserConfig:
    """Конфигурация QueryDenoiser-операции.

    :param lang: Язык, который будет использоваться в подаваемом на вход тексте. На основании выбранного языка будут использоваться соответствующие промпты при инференсе LLM-агента. Если 'auto', то язык определяется автоматически. Значение по умолчанию 'auto'.
    :type lang: str, optional
    :param agent_gen_stategy: Стратегия генерации текста для используемого LLM-агента. В случае None-значение будет использоваться стратегия по умолчанию. Значение по умолчанию None.
    :type agent_gen_stategy: Union[None,Dict[str, Union[str, int, float]]], optional
    :param swremoval_agent_task_config: Конфигурация атомарной задачи для LLM-агента по удалению излишней/ненужной информации из запроса. Значение по умолчанию DEFAULT_SWREMV_TASK_CONFIG.
    :type swremoval_agent_task_config: AgentTaskSolverConfig, optional
    :param grammarcheck_agent_task_config: Конфигурация атомарной задачи для LLM-агента по корректировке/переформулированию запроса в соответствии с грамматикой и синтаксисом используемого естественного языка. Значение по умолчанию DEFAULT_GRAMCHECK_TASK_CONFIG.
    :type grammarcheck_agent_task_config: AgentTaskSolverConfig, optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы QueryDenoiser-класса. Значение по умолчанию 'qp_denoising_stage_cache'.
    :type cache_table_name: str, optional
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты. Значение по умолчанию Logger(QD_MAIN_LOG_PATH).
    :type log: Logger, optional
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool, optional
    """
    lang: str = "auto"
    agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]] = None
    swremoval_agent_task_config: AgentTaskSolverConfig = field(
        default_factory=lambda: DEFAULT_SWREMV_TASK_CONFIG)
    grammarcheck_agent_task_config: AgentTaskSolverConfig = field(
        default_factory=lambda: DEFAULT_GRAMCHECK_TASK_CONFIG)

    cache_table_name: str = 'qp_denoising_stage_cache'
    log: Logger = field(default_factory=lambda: Logger(QD_MAIN_LOG_PATH))
    verbose: bool = False

    def to_str(self):
        return f"{self.lang}|{self.agent_gen_stategy}|{self.swremoval_agent_task_config.version}|{self.grammarcheck_agent_task_config.version}"


class QueryDenoiser(CacheUtils, AbstractCacheInfo):
    """Класс, реализующий одну из операций по форматированию/предобработке user-вопроса в рамках QueryPreprocessor-стадии. Данный класс выполняет удаление лишних шумов/фрагментов информации из user-вопроса.

    :param agent: Коннектор к конкретному LLM-агенту для выполнения inference-операций.
    :type agent: AbstractAgentConnector
    :param config: Конфигурация QueryDenoiser-операции. Значение по умолчанию QueryDenoiserConfig().
    :type config: QueryDenoiserConfig, optional
    :param cache_kvdriver_config:Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: KeyValueDriverConfig, optional
    :param cache_llm_inference: Если True, то все результаты решения атомарных LLM-задач будут кешироваться, иначе False. Значение по умолчанию True.
    :type cache_llm_inference: bool, optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операциий в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    """

    def __init__(self, agent: AbstractAgentConnector, config: QueryDenoiserConfig = QueryDenoiserConfig(),
                 cache_kvdriver_config: KeyValueDriverConfig = None, cache_llm_inference: bool = True,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None):
        self.config = config
        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, config.cache_table_name)

        self.agent = agent
        agents_cache_config = None
        if cache_llm_inference:
            agents_cache_config = cache_kvdriver_config if cache_llm_inference else None

        self.tasks_solvers: Dict[str, AgentTaskSolver] = dict()
        # удаление слов/знаков, мешающих/усложняющих пониманию/анализу основного смысла/намерения
        self.tasks_solvers['swremoval_solver'] = AgentTaskSolver(
            self.agent, self.config.swremoval_agent_task_config,
            agents_cache_config, inferencestat_config)
        # лингвистическая корректировка
        self.tasks_solvers['grammar_check_solver'] = AgentTaskSolver(
            self.agent, self.config.grammarcheck_agent_task_config,
            agents_cache_config, inferencestat_config)

        self.log = self.config.log
        self.verbose = self.config.verbose

    def get_agent_tgen_stat(self) -> Union[None, Dict[str, Union[None, Dict]]]:
        return {name: solver.get_agent_tgen_stat() for name, solver in self.tasks_solvers.items()}

    def get_cache_stat(self) -> Dict[str, Union[None, Dict]]:
        cache_stat = {'QueryDenoiser': None if self.cachekv is None else self.cachekv.kv_conn.count_items()}
        tasks_caches = {name: solver.get_cache_stat() for name, solver in self.tasks_solvers.items()}
        cache_stat.update(tasks_caches)
        return cache_stat

    def clear_kv_caches(self, level: str = 'all') -> None:
        if not isinstance(level, str):
            raise TypeError(
                f"Аргумент переменной 'level' должен иметь тип 'str'; сейчас аргумент имеет тип '{type(level)}'")
        if level not in ['all', 'current', 'other']:
            raise ValueError(
                f"Аргумент переменной 'level' должен принимать одно из трёх значенией: 'all', 'current' или 'other'. Полученное значение: '{level}'")

        if level in ['all', 'current']:
            self.cachekv.clear()
            self.tasks_solvers['swremoval_solver'].cachekv.clear()
            self.tasks_solvers['grammar_check_solver'].cachekv.clear()

        elif level == 'other':
            raise NotImplementedError

    def get_cache_key(self, query_info: QueryPreprocessingInfo) -> List[object]:
        str_using_agent_info = f"{self.agent.CONNECTOR_KW}:{self.agent.config.to_str()}"
        return [query_info.to_str(), self.config.to_str(), str_using_agent_info]

    @CacheUtils.cache_method_output
    def perform(self, query_info: QueryPreprocessingInfo) -> Tuple[str, ReturnInfo]:
        """Метод предназначен для выполнения операции форматирования/предобработки user-вопроса: декомпозиции сложных/составных user-вопросов на независимые/простые под-вопросы.

        :param query_info: Струкутра данных с результатами предыдущих операций предобратки/форматирования исходного user-вопроса.
        :type query_info: QueryPreprocessingInfo
        :return: Кортеж из двух объектов: (1) модифицированный user-вопрос без информации, зашумляющий основной запрос/интент; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[str, ReturnInfo]
        """
        self.log("START QUERY DENOISING...", verbose=self.config.verbose)
        self.log(
            f"BASE_QUESTION ID: {create_id(query_info.base_query)}", verbose=self.config.verbose)
        self.log(f"QUERY INFO: {query_info}", verbose=self.config.verbose)
        denoised_query, rinfo = None, ReturnInfo()

        if query_info.base_query is not None:
            query = query_info.base_query
        else:
            raise ValueError

        self.log("Выполнение удаление лишней информации/символов из запроса с помощью LLM-агента...",
                 verbose=self.config.verbose)
        query_wo_stopwords, status = self.tasks_solvers['swremoval_solver'].solve(
            lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, query=query)
        if status != ReturnStatus.success:
            rinfo.occurred_warning.append(status)
        else:
            self.log(f"RESULT: {query_wo_stopwords}",
                     verbose=self.config.verbose)

        if status == ReturnStatus.success:
            self.log("Выполнение перефразирования запроса с соблюдением грамматики и синтаксиса используемого естественного языке с помощью LLM-агента...", verbose=self.config.verbose)
            reformulated_query, status = self.tasks_solvers['grammar_check_solver'].solve(
                lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy,
                query=query_wo_stopwords)
            if status != ReturnStatus.success:
                rinfo.occurred_warning.append(status)
            else:
                self.log(f"RESULT: {reformulated_query}",
                         verbose=self.config.verbose)
                denoised_query = reformulated_query

        if denoised_query is None:
            rinfo.status = ReturnStatus.empty_answer
            rinfo.message = STATUS_MESSAGE[rinfo.status]

        self.log(f"RESULT: {denoised_query}", verbose=self.config.verbose)
        self.log(f"STATUS: {rinfo.status}", verbose=self.config.verbose)

        return denoised_query, rinfo
