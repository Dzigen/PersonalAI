from dataclasses import dataclass, field
from typing import Tuple, List, Union, Dict

from .config import ENEXTR_MAIN_LOG_PATH, DEFAULT_ENT_EXTR_TASK_CONFIG
from .utils import MediumEntitiesExtractorTaskSolvers
from ......utils import ReturnInfo, Logger, AgentTaskSolverConfig, AgentTaskSolver
from ......utils import ReturnStatus
from ......agents.utils import AbstractAgentConnector
from ......utils.data_structs import create_id, BaseComponentConfig, LanguageConfig
from ......db_drivers.kv_driver import KeyValueDriverConfig
from ......utils.cache_kv import CacheUtils
from ......utils.agent_stat_analyzer import AgentStatAnalyzerConfig
from ......utils.cache_kv.CacheOperations import CacheOperations
from ......utils.agent_stat_analyzer.AgentStatOperations import AgentStatOperations


@dataclass
class EntitiesExtractorConfig(BaseComponentConfig, LanguageConfig):
    """Конфигурация EntitiesExtractor-стадии MediumQA-ризонера.

    :param agent_gen_stategy: Стратегия генерации текста для используемого LLM-агента. В случае None-значение будет использоваться стратегия по умолчанию. Значение по умолчанию None.
    :type agent_gen_stategy: Union[None,Dict[str, Union[str, int, float]]], optional
    :param entities_extraction_agent_task_config: Конфигурация атомарной задачи для LLM-агента по извлечению сущностей из поискового запроса. Значение по умолчанию DEFAULT_ENT_EXTR_TASK_CONFIG.
    :type entities_extraction_agent_task_config: AgentTaskSolverConfig, optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы EntitiesExtractor-класса. Значение по умолчанию 'medreasn_entextr_main_stage_cache'.
    :type cache_table_name: str, optional
    """
    agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]] = None
    entities_extraction_agent_task_config: AgentTaskSolverConfig = field(
        default_factory=lambda: DEFAULT_ENT_EXTR_TASK_CONFIG)

    cache_table_name: str = "medreasn_entextr_main_stage_cache"
    log: Logger = field(default_factory=lambda: Logger(ENEXTR_MAIN_LOG_PATH))

    def to_str(self):
        return f"{self.lang}|{self.agent_gen_stategy}|{self.entities_extraction_agent_task_config.version}"


class EntitiesExtractor(CacheUtils, CacheOperations, AgentStatOperations):
    """Верхнеуровневый класс стадии #2.1.1 MediumQA-конвейера для извлечения сущностей из поискового запроса.

    :param agent: Коннектор к конкретному LLM-агенту для выполнения inference-операций.
    :type agent: AbstractAgentConnector
    :param config: Конфигурация EntitiesExtractor-стадии. Значение по умолчанию EntitiesExtractorConfig().
    :type config: EntitiesExtractorConfig, optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: KeyValueDriverConfig, optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операциий в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    :param cache_llm_inference: Если True, то все результаты решения атомарных LLM-задач будут кешироваться, иначе False. Значение по умолчанию True.
    :type cache_llm_inference: bool, optional
    """

    def __init__(self, agent: AbstractAgentConnector, config: EntitiesExtractorConfig = EntitiesExtractorConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None,
                 cache_llm_inference: bool = True):
        self.config = config

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, config.cache_table_name)

        self.agent = agent
        agents_cache_config = None
        if cache_llm_inference:
            agents_cache_config = cache_kvdriver_config

        self.tasks_solvers: MediumEntitiesExtractorTaskSolvers = MediumEntitiesExtractorTaskSolvers(
            entities_extractor_solver=AgentTaskSolver(
                self.agent, self.config.entities_extraction_agent_task_config, agents_cache_config, inferencestat_config)
        )

        self.log = self.config.log
        self.verbose = self.config.verbose

    def get_cache_key(self, query: str) -> List[str]:
        str_using_agent_info = f"{self.agent.CONNECTOR_KW}:{self.agent.config.to_str()}"
        return [query, self.config.to_str(), str_using_agent_info]

    @CacheUtils.cache_method_output
    def perform(self, query: str) -> Tuple[List[str], ReturnInfo]:
        """Метод предназначен для извлечения сущностей из поискового запроса на естественном языке.

        :param query: Поисковый запрос на естественном языке.
        :type query: str
        :return: Кортеж из двух объектов: (1) извлечённый список сущностей; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[List[str], ReturnInfo]
        """
        self.log("START ENTITIES EXTRACTION...", verbose=self.config.verbose)
        info = ReturnInfo()
        self.log(f"QUERY ID: {create_id(query)}", verbose=self.config.verbose)
        self.log(f"QUERY: {query}", verbose=self.config.verbose)

        self.log("Выполнение извлечения сущностей из запроса с помощью LLM-агента...",
                 verbose=self.config.verbose)
        entities, info.status = self.tasks_solvers.entities_extractor_solver.solve(
            lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, query=query)
        self.log(f"RESULT: {entities}", verbose=self.verbose)
        self.log(f"STATUS: {info.status}", verbose=self.verbose)

        if entities is None or len(entities) < 1:
            info.status = ReturnStatus.empty_answer

        return entities, info
