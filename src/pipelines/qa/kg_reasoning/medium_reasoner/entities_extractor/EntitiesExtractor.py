from dataclasses import dataclass, field
from typing import Tuple, List, Union, Dict
from copy import deepcopy

from .config import ENEXTR_MAIN_LOG_PATH
from .utils import MediumEntitiesExtractorTaskSolvers, EntitiesExtractorAgentTasksConfig
from ......utils import ReturnInfo, Logger, AgentTaskSolver, ReturnStatus, accumulate_stage_info, \
    CompositeModuleDetailedResult, ModuleType
from ......agents.utils import AbstractAgentConnector
from ......utils.data_structs import create_id, BaseComponentConfig, LanguageConfig
from ......utils.errors import STATUS_MESSAGE
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
    :param agent_tasks_config: Конфигурации LLM-промптов для решения заданных задач с помощью LLM-агента. Значение по умолчанию EntitiesExtractorAgentTasksConfig().
    :type agent_tasks_config: Union[EntitiesExtractorAgentTasksConfig, Dict], optional
    :param max_entities: Максимальное количество сущностей, которое может быть извлечено из заданного текста на естественном языке. Значение по кмолчанию 20.
    :type max_entities: int, optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы EntitiesExtractor-класса. Значение по умолчанию 'medreasn_entextr_main_stage_cache'.
    :type cache_table_name: str, optional
    """
    agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]] = None
    agent_tasks_config: Union[EntitiesExtractorAgentTasksConfig, Dict] = field(default_factory=lambda: EntitiesExtractorAgentTasksConfig())
    max_entities: int = 20

    cache_table_name: str = "medreasn_entextr_main_stage_cache"
    log_path: str = ENEXTR_MAIN_LOG_PATH

    def to_str(self):
        return f"{self.lang}|{self.agent_gen_stategy}|{self.max_entities}|{self.agent_tasks_config.to_str()}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = EntitiesExtractorConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.agent_tasks_config, dict):
            self.agent_tasks_config = EntitiesExtractorAgentTasksConfig.from_dict(self.agent_tasks_config)


class EntitiesExtractor(CacheUtils, CacheOperations, AgentStatOperations):
    """Верхнеуровневый класс стадии #2.1.1 MediumQA-конвейера для извлечения сущностей из поискового запроса.

    :param agent: Коннектор к конкретному LLM-агенту для выполнения inference-операций.
    :type agent: AbstractAgentConnector
    :param config: Конфигурация EntitiesExtractor-стадии. Значение по умолчанию EntitiesExtractorConfig().
    :type config: Union[EntitiesExtractorConfig, Dict], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: KeyValueDriverConfig, optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операциий в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    :param cache_llm_inference: Если True, то все результаты решения атомарных LLM-задач будут кешироваться, иначе False. Значение по умолчанию True.
    :type cache_llm_inference: bool, optional
    """

    def __init__(self, agent: AbstractAgentConnector, config: Union[EntitiesExtractorConfig, Dict] = EntitiesExtractorConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None,
                 cache_llm_inference: bool = True):
        if isinstance(config, dict):
            config: EntitiesExtractorConfig = EntitiesExtractorConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config = config
        self.config.agent_tasks_config.versions_to_configs(self.config.verbose, self.config.log_level)

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, config.cache_table_name)

        self.agent = agent
        agents_cache_config = None
        if cache_llm_inference:
            agents_cache_config = cache_kvdriver_config

        self.tasks_solvers: MediumEntitiesExtractorTaskSolvers = MediumEntitiesExtractorTaskSolvers(
            entities_extractor_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.entities_extraction, agents_cache_config, inferencestat_config)
        )

        self.log = Logger(config.log_path)
        self.verbose = self.config.verbose
        self.log_level = self.config.log_level

    def get_cache_key(self, query: str) -> List[str]:
        str_using_agent_info = f"{self.agent.CONNECTOR_KW}:{self.agent.config.to_str()}"
        return [query, self.config.to_str(), str_using_agent_info]

    @accumulate_stage_info
    @CacheUtils.cache_method_output
    def perform(self, query: str) -> Tuple[List[str], ReturnInfo, CompositeModuleDetailedResult]:
        """Метод предназначен для извлечения сущностей из поискового запроса на естественном языке.

        :param query: Поисковый запрос на естественном языке.
        :type query: str
        :return: Кортеж из трёх объектов: (1) извлечённый список сущностей; (2) статус завершения операции с пояснительной информацией; (3) структура данных с промежуточными результатами реботы метода.
        :rtype: Tuple[List[str], ReturnInfo, CompositeModuleDetailedResult]
        """
        self.log.debug("START ENTITIES EXTRACTION...", verbose=self.verbose, log_level=self.log_level)
        rinfo, module_trace = ReturnInfo(), CompositeModuleDetailedResult()
        self.log.debug("* Query hash: %s", create_id(query), verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Query: %s", query, verbose=self.verbose, log_level=self.log_level)

        self.log.debug("Выполнение извлечения сущностей из запроса с помощью LLM-агента...", verbose=self.verbose, log_level=self.log_level)
        extracted_entities, rinfo.status, trace = self.tasks_solvers.entities_extractor_solver.solve(
            lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, query=query)
        module_trace.add("entities_extractor_solver", ModuleType.task_solver, trace)

        entities = []
        if extracted_entities is None or len(extracted_entities) == 0:
            rinfo.status = ReturnStatus.zero_entities
            rinfo.message = STATUS_MESSAGE[rinfo.status]
        else:
            self.log.debug("Количество извлечённых сущностей, до урезания: %d", len(extracted_entities), verbose=self.verbose, log_level=self.log_level)
            self.log.debug("TMP_RESULT: %s", extracted_entities, verbose=self.verbose, log_level=self.log_level)
            entities = extracted_entities[:self.config.max_entities]
            self.log.debug("RESULT: %s", len(entities), verbose=self.verbose, log_level=self.log_level)
            for entity in entities:
                self.log.debug("* %s", entity, verbose=self.verbose, log_level=self.log_level)

        self.log.debug("STATUS: %s", STATUS_MESSAGE[rinfo.status], verbose=self.verbose, log_level=self.log_level)

        return entities, rinfo, module_trace
