from dataclasses import dataclass, field
from typing import Tuple, List, Union, Dict

from .config import QD_MAIN_LOG_PATH, DEFAULT_QD_TASK_CONFIG, DEFAULT_DC_TASK_CONFIG
from ..QueryPreprocessor import QueryPreprocessingInfo
from .....utils.cache_kv import CacheUtils
from .....utils.errors import STATUS_MESSAGE
from .....utils.data_structs import create_id
from .....agents.utils import AbstractAgentConnector
from .....utils import ReturnInfo, Logger, ReturnStatus, AgentTaskSolverConfig, AgentTaskSolver
from .....db_drivers.kv_driver import KeyValueDriverConfig


@dataclass
class QueryDecomposerConfig:
    """Конфигурация QueryDecomposer-операции.

    :param lang: Язык, который будет использоваться в подаваемом на вход тексте. На основании выбранного языка будут использоваться соответствующие промпты при инференсе LLM-агента. Если 'auto', то язык определяется автоматически. Значение по умолчанию 'auto'.
    :type lang: str, optional
    :param agent_gen_stategy: Стратегия генерации текста для используемого LLM-агента. В случае None-значение будет использоваться стратегия по умолчанию. Значение по умолчанию None.
    :type agent_gen_stategy: Union[None,Dict[str, Union[str, int, float]]], optional
    :param classify_agent_task_config: Конфигурация атомарной задачи для LLM-агента по классификации наличия независимых запросов (составности/сложности) в user-вопросе. Значение по умолчанию DEFAULT_DC_TASK_CONFIG.
    :type classify_agent_task_config: AgentTaskSolverConfig, optional
    :param decompose_agent_task_config: Конфигурация атомарной задачи для LLM-агента по разбиению user-вопроса на независимые/простые под-вопросы. Значение по умолчанию DEFAULT_QD_TASK_CONFIG.
    :type decompose_agent_task_config: AgentTaskSolverConfig, optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы QueryDecomposer-класса. Значение по умолчанию 'qp_decomposition_stage_cache'.
    :type cache_table_name: str, optional
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты. Значение по умолчанию Logger(QD_MAIN_LOG_PATH).
    :type log: Logger, optional
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool, optional
    """
    lang: str = "auto"
    agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]] = None
    classify_agent_task_config: AgentTaskSolverConfig = field(
        default_factory=lambda: DEFAULT_DC_TASK_CONFIG)
    decompose_agent_task_config: AgentTaskSolverConfig = field(
        default_factory=lambda: DEFAULT_QD_TASK_CONFIG)

    cache_table_name: str = 'qp_decomposition_stage_cache'
    log: Logger = field(default_factory=lambda: Logger(QD_MAIN_LOG_PATH))
    verbose: bool = False

    def to_str(self):
        return f"{self.lang}|{self.agent_gen_stategy}|{self.classify_agent_task_config.version}|{self.decompose_agent_task_config.version}"


class QueryDecomposer(CacheUtils):
    """Класс, реализующий одну из операций по форматированию/предобработке user-вопроса в рамках QueryPreprocessor-стадии. Данный класс выполняет декомпозицию сложного/составного user-вопроса на независимые/простые под-вопросы.

    :param agent: Коннектор к конкретному LLM-агенту для выполнения inference-операций.
    :type agent: AbstractAgentConnector
    :param config: Конфигурация QueryDecomposer-операции. Значение по умолчанию QueryDecomposerConfig().
    :type config: QueryDecomposerConfig, optional
    :param cache_kvdriver_config:Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: KeyValueDriverConfig, optional
    :param cache_llm_inference: Если True, то все результаты решения атомарных LLM-задач будут кешироваться, иначе False. Значение по умолчанию True.
    :type cache_llm_inference: bool, optional
    """

    def __init__(self, agent: AbstractAgentConnector, config: QueryDecomposerConfig = QueryDecomposerConfig(),
                 cache_kvdriver_config: KeyValueDriverConfig = None, cache_llm_inference: bool = True):
        self.config = config
        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, config.cache_table_name)

        self.agent = agent
        agents_cache_config = None
        if cache_llm_inference:
            agents_cache_config = cache_kvdriver_config if cache_llm_inference else None

        self.decompose_classifier_solver = AgentTaskSolver(
            self.agent, self.config.classify_agent_task_config, agents_cache_config)
        self.q_decomposition_solver = AgentTaskSolver(
            self.agent, self.config.decompose_agent_task_config, agents_cache_config)

        self.log = self.config.log
        self.verbose = self.config.verbose

    def clear_kv_caches(self, level: str = 'all') -> None:
        if not isinstance(level, str):
            raise TypeError(
                f"Аргумент переменной 'level' должен иметь тип 'str'; сейчас аргумент имеет тип '{type(level)}'")
        if level not in ['all', 'current', 'other']:
            raise ValueError(
                f"Аргумент переменной 'level' должен принимать одно из трёх значенией: 'all', 'current' или 'other'. Полученное значение: '{level}'")

        if level in ['all', 'current']:
            self.cachekv.clear()
            self.decompose_classifier_solver.cachekv.clear()
            self.q_decomposition_solver.cachekv.clear()

        elif level == 'other':
            raise NotImplementedError

    def get_cache_key(self, query_info: QueryPreprocessingInfo) -> List[str]:
        str_using_agent_info = f"{self.agent.CONNECTOR_KW}:{self.agent.config.to_str()}"
        return [query_info.to_str(), self.config.to_str(), str_using_agent_info]

    @CacheUtils.cache_method_output
    def perform(self, query_info: QueryPreprocessingInfo) -> Tuple[List[str], ReturnInfo]:
        """Метод предназначен для выполнения операции форматирования/предобработки user-вопроса: декомпозиции сложных/составных user-вопросов на независимые/простые под-вопросы.

        :param query_info: Струкутра данных с результатами предыдущих операций предобратки/форматирования исходного user-вопроса.
        :type query_info: QueryPreprocessingInfo
        :return: Кортеж из двух объектов: (1) список простых под-вопросов для исходного/сложного user-вопроса; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[str, ReturnInfo]
        """
        self.log("START QUERY DECOMPOSITION...", verbose=self.config.verbose)
        self.log(
            f"BASE_QUESTION ID: {create_id(query_info.base_query)}", verbose=self.config.verbose)
        self.log(f"QUERY INFO: {query_info}", verbose=self.config.verbose)
        decomposed_query, rinfo = None, ReturnInfo()

        if query_info.enchanced_query is not None:
            query = query_info.enchanced_query
        elif query_info.denoised_query is not None:
            query = query_info.denoised_query
        elif query_info.base_query is not None:
            query = query_info.base_query
        else:
            raise ValueError

        self.log("Выполнение проверки на необходимость декомпозии вопроса с помощью LLM-агента...",
                 verbose=self.config.verbose)
        need_to_decompose, status = self.decompose_classifier_solver.solve(
            lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy,
            query=query)
        if status != ReturnStatus.success:
            rinfo.occurred_warning.append(status)

        if status == ReturnStatus.success:
            if need_to_decompose:
                self.log("Выполнение разбиения вопроса на независимые под-вопросы с помощью LLM-агента...",
                         verbose=self.config.verbose)
                decomposed_query, status = self.q_decomposition_solver.solve(
                    lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, query=query)
                if status != ReturnStatus.success:
                    rinfo.occurred_warning.append(status)
            else:
                self.log("Выполнение декомпозиции вопроса не требуется",
                         verbose=self.config.verbose)
                rinfo.occurred_warning.append(ReturnStatus.decompose_noneed)
                decomposed_query = [query]

        if decomposed_query is None:
            rinfo.status = ReturnStatus.empty_answer
            rinfo.message = STATUS_MESSAGE[rinfo.status]

        self.log(f"RESULT: {decomposed_query}", verbose=self.config.verbose)
        self.log(f"STATUS: {rinfo.status}", verbose=self.config.verbose)

        return decomposed_query, rinfo
