from dataclasses import dataclass, field
from typing import Tuple, Union, List, Dict
from copy import deepcopy

from .config import AAGG_MAIN_LOG_PATH
from .utils import AnswerAggregatorTaskSolvers, AnswersAggregatorAgentTasksConfig
from ..kg_reasoning.utils import QueryReasoningInfo
from ....utils import ReturnInfo, Logger, AgentTaskSolver, \
    accumulate_stage_info, CompositeModuleDetailedResult, ModuleType
from ....agents.utils import AbstractAgentConnector
from ....utils.data_structs import create_id, QueryPreprocessingInfo, BaseComponentConfig, LanguageConfig
from ....db_drivers.kv_driver import KeyValueDriverConfig
from ....utils.cache_kv import CacheUtils
from ....utils.cache_kv.CacheOperations import CacheOperations
from ....utils.agent_stat_analyzer.AgentStatOperations import AgentStatOperations
from ....utils.agent_stat_analyzer import AgentStatAnalyzerConfig


@dataclass
class AnswersAggregatorConfig(BaseComponentConfig, LanguageConfig):
    """Конфигурация AnswersAggregator-стадии.

    :param agent_gen_stategy: Стратегия генерации текста для используемого LLM-агента. В случае None-значения будет использоваться стратегия по умолчанию. Значение по умолчанию None.
    :type agent_gen_stategy: Union[None,Dict[str, Union[str, int, float]]], optional
    :param agent_tasks_config: Конфигурации LLM-промптов для решения заданных задач с помощью LLM-агента. Значение по умолчанию AnswersAggregatorAgentTasksConfig().
    :type agent_tasks_config: Union[Dict, AnswersAggregatorAgentTasksConfig], optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы AnswersAggregator-класса. Значение по умолчанию 'answers_aggregation_main_stage_cache'.
    :type cache_table_name: str, optional
    """
    agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]] = None
    agent_tasks_config: Union[Dict, AnswersAggregatorAgentTasksConfig] = field(default_factory=lambda: AnswersAggregatorAgentTasksConfig())

    cache_table_name: str = 'answers_aggregation_main_stage_cache'
    log: Logger = field(default_factory=lambda: Logger(AAGG_MAIN_LOG_PATH))

    def to_str(self) -> str:
        return f"{self.lang}|{self.agent_gen_stategy}|{self.agent_tasks_config.to_str()}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = AnswersAggregatorConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.agent_tasks_config, dict):
            self.agent_tasks_config = AnswersAggregatorAgentTasksConfig.from_dict(self.agent_tasks_config)


class AnswersAggregator(CacheUtils, CacheOperations, AgentStatOperations):
    """Верхнеуровневый класс AnswersAggregator-стадии (точка входа), отвечающей за аггрегацию/резюмирование информации, полученной в результате ризонинга на графе знаний (памяти), и генерацию финального ответа на user-вопрос.

    :param agent: Коннектор к конкретному LLM-агенту для выполнения inference-операций.
    :type agent: AbstractAgentConnector
    :param config: Конфигурация AnswersAggregator-стадии. Значение по умолчанию AnswersAggregatorConfig().
    :type config: AnswersAggregatorConfig, optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    :param cache_llm_inference: Если True, то все результаты решения атомарных LLM-задач будут кешироваться, иначе False. Значение по умолчанию True.
    :type cache_llm_inference: bool, optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операций в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    """

    def __init__(self, agent: AbstractAgentConnector, config: Union[Dict, AnswersAggregatorConfig] = AnswersAggregatorConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None, cache_llm_inference: bool = True,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None) -> None:
        if isinstance(config, dict):
            config: AnswersAggregatorConfig = AnswersAggregatorConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config = config
        self.config.agent_tasks_config.versions_to_configs()

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, config.cache_table_name)

        self.agent = agent
        agents_cache_config = None
        if cache_llm_inference:
            agents_cache_config = cache_kvdriver_config

        self.tasks_solvers: AnswerAggregatorTaskSolvers = AnswerAggregatorTaskSolvers(
            subanswers_summarisation_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.suba_summarisation, agents_cache_config, inferencestat_config
            )
        )

        self.log = self.config.log
        self.verbose = self.config.verbose

    def get_cache_key(self, query_info: QueryPreprocessingInfo, subq_info: QueryReasoningInfo) -> List[str]:
        """Формирует ключ кэша для результатов агрегации ответов.

        В ключ включается сериализованное представление предобработанного запроса, сериализованное представление под-вопросов и их ответов, строковое представление конфигурации агрегатора, идентификатор и конфигурацию используемого LLM-агента.

        :param query_info: Структура с предобработанным user-вопросом.
        :type query_info: QueryPreprocessingInfo
        :param subq_info: Структура с под-вопросами и их ответами.
        :type subq_info: QueryReasoningInfo
        :return: Список строк, используемый как составной ключ кеша.
        :rtype: List[str]
        """
        str_using_agent_info = f"{self.agent.CONNECTOR_KW}:{self.agent.config.to_str()}"
        return [query_info.to_str(), subq_info.to_str(), self.config.to_str(), str_using_agent_info]

    @accumulate_stage_info
    @CacheUtils.cache_method_output
    def perform(self, query_info: QueryPreprocessingInfo, subq_info: QueryReasoningInfo) -> Tuple[str, ReturnInfo, CompositeModuleDetailedResult]:
        """Метод предназначен для выполнения операции аггрегации/резюмирования информации, полученной в результате ризонинга на графе знаний (памяти), и генерации финального ответа на user-вопрос.

        :param query_info: Структура данных с предобработанным user-вопросом и результатами промежуточных операций по его форматированию.
        :type query_info: QueryPreprocessingInfo
        :param subq_info: Структура данных с извлечённой из графа знаний информацией по предобработанному user-вопросу для генерации ответа.
        :type subq_info: QueryReasoningInfo
        :return: Кортеж из трёх объектов: (1) финальный ответ на user-вопрос; (2) статус завершения операции с пояснительной информацией; (3) структура данных с промежуточными результатами реботы метода.
        :rtype: Tuple[str, ReturnInfo, CompositeModuleDetailedResult]
        """
        self.log("START ANSWERS AGGREGATION...", verbose=self.verbose)
        self.log(f"BASE_QUESTION ID: {create_id(query_info.base_query)}", verbose=self.verbose)
        self.log(f"QUERY_INFO: {query_info}", verbose=self.verbose)
        self.log(f"SUB_ANSWERS: {subq_info.sub_answers}", verbose=self.verbose)
        final_answer, rinfo, module_trace = None, ReturnInfo(), CompositeModuleDetailedResult()

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

            self.log("Выполнение суммаризации ответов с помощью LLM-агента...", verbose=self.verbose)
            final_answer, status, trace = self.tasks_solvers.subanswers_summarisation_solver.solve(
                lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy,
                query=query, sub_queries=sub_queries, sub_answers=subq_info.sub_answers)
            self.log(f"RESULT: {final_answer}", verbose=self.verbose)
            module_trace.add("subanswers_summarisation_solver", ModuleType.task_solver, trace)
            rinfo.status = status

        self.log(f"STATUS: {rinfo.status}", verbose=self.verbose)

        return final_answer, rinfo, module_trace
