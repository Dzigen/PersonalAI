from dataclasses import dataclass, field
from typing import Tuple, Union, List, Dict

from .config import AAGG_MAIN_LOG_PATH, DEFAULT_SUBASUMM_TASK_CONFIG
from .utils import AnswerAggregatorTaskSolvers
from ..kg_reasoning.utils import QueryReasoningInfo
from ....utils import ReturnInfo, Logger, AgentTaskSolverConfig, AgentTaskSolver
from ....agents.utils import AbstractAgentConnector
from ....utils.data_structs import create_id, QueryPreprocessingInfo
from ....db_drivers.kv_driver import KeyValueDriverConfig
from ....utils.cache_kv import CacheUtils
from ....utils.cache_kv.CacheOperations import CacheOperations
from ....utils.agent_stat_analyzer.AgentStatOperations import AgentStatOperations
from ....utils.agent_stat_analyzer import AgentStatAnalyzerConfig


@dataclass
class AnswersAggregatorConfig:
    """Конфигурация AnswersAggregator-стадии.

    :param lang: Язык, который будет использоваться в подаваемом на вход тексте. На основании выбранного языка будут использоваться соответствующие промпты при инференсе LLM-агента. Если 'auto', то язык определяется автоматически. Значение по умолчанию 'auto'.
    :type lang: str, optional
    :param agent_gen_stategy: Стратегия генерации текста для используемого LLM-агента. В случае None-значение будет использоваться стратегия по умолчанию. Значение по умолчанию None.
    :type agent_gen_stategy: Union[None,Dict[str, Union[str, int, float]]], optional
    :param suba_summarisation_agent_task_config: Конфигурация атомарной задачи для LLM-агента по суммаризации/объединению независимых ответов на под-вопросы в один финальный ответ на исходный user-вопрос. Значение по умолчанию DEFAULT_SUBASUMM_TASK_CONFIG.
    :type suba_summarisation_agent_task_config: AgentTaskSolverConfig, optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы AnswersAggregator-класса. Значение по умолчанию 'answers_aggregation_main_stage_cache'.
    :type cache_table_name: str, optional
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты. Значение по умолчанию Logger(AAGG_MAIN_LOG_PATH).
    :type log: Logger, optional
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool, optional
    """
    lang: str = 'auto'
    agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]] = None
    suba_summarisation_agent_task_config: AgentTaskSolverConfig = field(default_factory=lambda: DEFAULT_SUBASUMM_TASK_CONFIG)

    cache_table_name: str = 'answers_aggregation_main_stage_cache'
    log: Logger = field(default_factory=lambda: Logger(AAGG_MAIN_LOG_PATH))
    verbose: bool = False

    def to_str(self) -> str:
        return f"{self.lang}|{self.agent_gen_stategy}|{self.suba_summarisation_agent_task_config.version}"


class AnswersAggregator(CacheUtils, CacheOperations, AgentStatOperations):
    """Верхнеуровневый класс QueryPreprocessor-стадии (точка входа), отвечающей за аггрегации/резюмированию информации, полученной в резльтате ризонинга на графе знаний (памяти), и генерацию финального ответа на user-вопрос.

    :param agent: Коннектор к конкретному LLM-агенту для выполнения inference-операций.
    :type agent: AbstractAgentConnector
    :param config: Конфигурация AnswersAggregator-стадии. Значение по умолчанию AnswersAggregatorConfig().
    :type config: AnswersAggregatorConfig, optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    :param cache_llm_inference: Если True, то все результаты решения атомарных LLM-задач будут кешироваться, иначе False. Значение по умолчанию True.
    :type cache_llm_inference: bool, optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операциий в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    """

    def __init__(self, agent: AbstractAgentConnector, config: AnswersAggregatorConfig = AnswersAggregatorConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None, cache_llm_inference: bool = True,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None) -> None:
        self.config = config

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, config.cache_table_name)

        self.agent = agent
        agents_cache_config = None
        if cache_llm_inference:
            agents_cache_config = cache_kvdriver_config

        self.tasks_solvers: AnswerAggregatorTaskSolvers = AnswerAggregatorTaskSolvers(
            subanswers_summarisation_solver=AgentTaskSolver(
                self.agent, self.config.suba_summarisation_agent_task_config, agents_cache_config, inferencestat_config
            )
        )

        self.log = self.config.log
        self.verbose = self.config.verbose

    def get_cache_key(self, query_info: QueryPreprocessingInfo, subq_info: QueryReasoningInfo) -> List[str]:
        str_using_agent_info = f"{self.agent.CONNECTOR_KW}:{self.agent.config.to_str()}"
        return [query_info.to_str(), subq_info.to_str(), self.config.to_str(), str_using_agent_info]

    @CacheUtils.cache_method_output
    def perform(self, query_info: QueryPreprocessingInfo, subq_info: QueryReasoningInfo) -> Tuple[str, ReturnInfo]:
        """Метод предназначен для выполнения операции аггрегации/резюмирования информации, полученной в резльтате ризонинга на графе знаний (памяти), и генерации финального ответа на user-вопрос.

        :param query_info: Струкутра данных с предобработанным user-вопросом и результами промежуточных операций по его форматированию.
        :type query_info: QueryPreprocessingInfo
        :param subq_info: Структура данных с извлечённой из графа знаний информацией по предобработанному user-вопросу для генерации ответа.
        :type subq_info: QueryReasoningInfo
        :return: Кортеж из двух объектов: (1) финальный ответ на user-вопрос; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[str, ReturnInfo]
        """
        self.log("START ANSWERS AGGREGATION...", verbose=self.config.verbose)
        self.log(f"BASE_QUESTION ID: {create_id(query_info.base_query)}", verbose=self.config.verbose)
        self.log(f"QUERY_INFO: {query_info}", verbose=self.config.verbose)
        self.log(f"SUB_ANSWERS: {subq_info.sub_answers}",
                 verbose=self.config.verbose)
        final_answer, info = None, ReturnInfo()

        if len(subq_info.sub_answers) < 0:
            raise ValueError
        elif len(subq_info.sub_answers) == 1:
            final_answer = subq_info.sub_answers[0]
        else:
            if query_info.enchanced_query is not None:
                query = query_info.enchanced_query
            elif query_info.denoised_query is not None:
                query = query_info.denoised_query
            elif query_info.base_query is not None:
                query = query_info.base_query
            else:
                raise ValueError

            sub_queries = query_info.decomposed_query
            if len(sub_queries) < 2 or len(subq_info.sub_answers) != len(sub_queries):
                raise ValueError

            self.log("Выполнение суммаризации ответов с помощью LLM-агента...",
                     verbose=self.config.verbose)
            final_answer, status = self.tasks_solvers.subanswers_summarisation_solver.solve(
                lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy,
                query=query, sub_queries=sub_queries,
                sub_answers=subq_info.sub_answers)
            self.log(f"RESULT: {final_answer}", verbose=self.verbose)
            info.status = status

        self.log(f"STATUS: {info.status}", verbose=self.verbose)

        return final_answer, info
