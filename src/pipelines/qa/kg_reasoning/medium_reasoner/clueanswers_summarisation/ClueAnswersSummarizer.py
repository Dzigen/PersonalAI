from dataclasses import dataclass, field
from typing import Tuple, Union, List, Dict
from copy import deepcopy

from .config import CQSUMM_MAIN_LOG_PATH
from .utils import MediumASummarizerTaskSolvers, ClueAnswersSummarizerAgentTasksConfig
from ......utils import ReturnInfo, Logger, AgentTaskSolver
from ......agents.utils import AbstractAgentConnector
from ......utils.data_structs import create_id, BaseComponentConfig, LanguageConfig
from ......db_drivers.kv_driver import KeyValueDriverConfig
from ......utils.cache_kv import CacheUtils
from ......utils.agent_stat_analyzer import AgentStatAnalyzerConfig
from ......utils.agent_stat_analyzer.AgentStatOperations import AgentStatOperations
from ......utils.cache_kv.CacheOperations import CacheOperations


@dataclass
class ClueAnswersSummarizerConfig(BaseComponentConfig, LanguageConfig):
    """Конфигурация ClueQueriesGenerator-стадии MediumQA-ризонера.

    :param agent_gen_stategy: Стратегия генерации текста для используемого LLM-агента. В случае None-значение будет использоваться стратегия по умолчанию. Значение по умолчанию None.
    :type agent_gen_stategy: Union[None,Dict[str, Union[str, int, float]]], optional
    :param agent_tasks_config: Конфигурации LLM-промптом для решения заданных задач с помощью LLM-агента. Значение по умолчанию ClueAnswersSummarizerAgentTasksConfig().
    :type agent_tasks_config: Union[ClueAnswersSummarizerAgentTasksConfig, Dict], optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы ClueAnswersSummarizer-класса. Значение по умолчанию 'medreasn_cquerysumm_main_stage_cache'.
    :type cache_table_name: str, optional
    """
    agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]] = None
    agent_tasks_config: Union[ClueAnswersSummarizerAgentTasksConfig, Dict] = field(default_factory=lambda: ClueAnswersSummarizerAgentTasksConfig())

    cache_table_name: str = "medreasn_cquerysumm_main_stage_cache"
    log: Logger = field(default_factory=lambda: Logger(CQSUMM_MAIN_LOG_PATH))

    def to_str(self):
        return f"{self.lang}|{self.agent_gen_stategy}|{self.agent_tasks_config.to_str()}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = ClueAnswersSummarizerConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.agent_tasks_config, dict):
            self.agent_tasks_config = ClueAnswersSummarizerAgentTasksConfig.from_dict(self.agent_tasks_config)


class ClueAnswersSummarizer(CacheUtils, AgentStatOperations, CacheOperations):
    """Верхнеуровневый класс стадии #3.2 MediumQA-конвейера для суммаризации/резюмирования информации, извлечённой из графа знаний (памяти ассистента) по search_query-шагу поиска.

    :param agent: Коннектор к конкретному LLM-агенту для выполнения inference-операций.
    :type agent: AbstractAgentConnector
    :param config: Конфигурация ClueAnswersSummarizer-стадии. Значение по умолчанию ClueAnswersSummarizerConfig().
    :type config: Union[ClueAnswersSummarizerConfig, Dict], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: KeyValueDriverConfig, optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операциий в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    :param cache_llm_inference: Если True, то все результаты решения атомарных LLM-задач будут кешироваться, иначе False. Значение по умолчанию True.
    :type cache_llm_inference: bool, optional
    """

    def __init__(self, agent: AbstractAgentConnector, config: Union[ClueAnswersSummarizerConfig, Dict] = ClueAnswersSummarizerConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None,
                 cache_llm_inference: bool = True,) -> None:
        if isinstance(config, dict):
            config: ClueAnswersSummarizerConfig = ClueAnswersSummarizerConfig.from_dict(config)
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

        self.tasks_solvers: MediumASummarizerTaskSolvers = MediumASummarizerTaskSolvers(
            clueanswers_summ_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.canswers_summarisation, agents_cache_config, inferencestat_config)
        )

        self.log = self.config.log
        self.verbose = self.config.verbose

    def get_cache_key(self, search_query: str, clue_queries: List[str], clue_answers: List[str]) -> List[str]:
        str_cluequeries = ';'.join(clue_queries)
        str_clueanswers = ';'.join(clue_answers)
        str_using_agent_info = f"{self.agent.CONNECTOR_KW}:{self.agent.config.to_str()}"
        return [search_query, str_cluequeries, str_clueanswers, str_using_agent_info]

    @CacheUtils.cache_method_output
    def perform(self, search_query: str, clue_queries: List[str], clue_answers: List[str]) -> Tuple[str, ReturnInfo]:
        """Метод предназначен для резюмирвоания информации, извлечённой из графа знаний (с помощью clue-запросов) для данного search_query-шага поиска (в рамках плана).

        :param search_query: Базовый шаг поиска (в рамках текущего плана) на естественном языке.
        :type search_query: str
        :param clue_queries: Список Clue-запросов на естественной языке.
        :type clue_queries: List[str]
        :param clue_answers: Список Clue-ответов, которые были сформированы в рамках обхода/поиска графа знаний с помощью соответствующих clue-запросов.
        :type clue_answers: List[str]
        :return: Кортеж из двух объектов: (1) резюмированный набор информации (в виде полносвязного текста на естественном языке), который является результатов поиска в графе знаний (памяти ассистента) по данному базовому шагу/запросу плана. (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[str, ReturnInfo]
        """
        self.log("START CLUE-QUERIES SUMMARISATION...", verbose=self.verbose)
        self.log(f"SEARCH_QUERY ID: {create_id(search_query)}", verbose=self.verbose)
        self.log(f"SEARCH_QUERY: {search_query}", verbose=self.verbose)
        self.log(f"CLUE-QUERIES: {clue_queries}", verbose=self.verbose)
        self.log(f"CLUE-ANSWERS: {clue_answers}", verbose=self.verbose)
        summ_answer, info = None, ReturnInfo()

        if len(search_query) < 1 or len(clue_queries) < 1 or len(clue_answers) != len(clue_queries):
            raise ValueError

        self.log("Выполненяем суммаризацию clue-answers с помощью LLM-агента...",
                 verbose=self.verbose)
        summ_answer, status = self.tasks_solvers.clueanswers_summ_solver.solve(
            lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, search_query=search_query,
            clues_queries=clue_queries, clue_answers=clue_answers)
        self.log(f"RESULT: {summ_answer}", verbose=self.verbose)

        info.status = status
        self.log(f"STATUS: {info.status}", verbose=self.verbose)

        return summ_answer, info
