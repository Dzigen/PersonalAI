from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Union
from copy import deepcopy

from .configs import DEFAULT_THESISES_EXTR_TASK_CONFIG, DEFAULT_TRIPLETS_EXTR_TASK_CONFIG, MEM_EXTRACTOR_MAIN_LOG_PATH, \
    AgentThesisExtrTaskConfigSelector, AgentTripletExtrTaskConfigSelector
from .utils import MemExtractorTaskSolvers
from ....utils import Logger, ReturnStatus, ReturnInfo, AgentTaskSolver, AgentTaskSolverConfig
from ....utils.errors import STATUS_MESSAGE
from ....utils.data_structs import TripletCreator, NodeCreator, Node, Relation, \
    RelationType, NodeType, Triplet, create_id, BaseComponentConfig, LanguageConfig
from ....agents.utils import AbstractAgentConnector
from ....db_drivers.kv_driver import KeyValueDriverConfig
from ....utils.cache_kv.CacheOperations import CacheOperations
from ....utils.agent_stat_analyzer import AgentStatAnalyzerConfig
from ....utils.agent_stat_analyzer.AgentStatOperations import AgentStatOperations


@dataclass
class LLMExtractorConfig(BaseComponentConfig, LanguageConfig):
    """Конфигурация Extractor-стадии Memorize-конвейера.

    :param agent_gen_stategy: Стратегия генерации текста для используемого LLM-агента. В случае None-значение будет использоваться стратегия по умолчанию. Значение по умолчанию None.
    :type agent_gen_stategy: Union[None,Dict[str, Union[str, int, float]]], optional
    :param triplets_extraction_task_config: Конфигурация атомарной задачи для LLM-агента по извлечению триплетов с информацией типа 'simple' из слабоструктурированных текстов на естественном языке. Значение по умолчанию DEFAULT_EXTRACT_TRIPLETS_TASK_CONFIG.
    :type triplets_extraction_task_config: AgentTaskSolverConfig
    :param thesises_extraction_task_config: Конфигурация атомарной задачи для LLM-агента по извлечению триплетов с информацией типа 'hyper' из слабоструктурированных текстов на естественном языке. Значение по умолчанию DEFAULT_EXTRACT_THESISES_TASK_CONFIG.
    :type thesises_extraction_task_config: AgentTaskSolverConfig
    :param need_simple: Если True, то из входного текста на первой стадии Mem-конвейера будет выполнено извлечение триплетов с типом связи 'simple', иначе False. Значение по умолчанию True.
    :type need_simple: bool, optional
    :param need_thesises: Если True, то из входного текста на первой стадии Mem-конвейера будет выполнено извлечение триплетов с типом связи 'hyper', иначе False. Значение по умолчанию True.
    :type need_thesises: bool, optional
    :param need_episodic: Если True, то из входного текста на первой стадии Mem-конвейера будет выполнено извлечение триплетов с типом связи 'episodic', иначе False. Значение по умолчанию True.
    :type need_episodic: bool, optional
    """
    agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]] = None
    triplets_extraction_task_config: Union[AgentTaskSolverConfig, str] = field(default_factory=lambda: DEFAULT_TRIPLETS_EXTR_TASK_CONFIG)
    thesises_extraction_task_config: Union[AgentTaskSolverConfig, str] = field(default_factory=lambda: DEFAULT_THESISES_EXTR_TASK_CONFIG)
    need_simple: bool = True
    need_thesises: bool = True
    need_episodic: bool = True

    log: Logger = field(default_factory=lambda: Logger(MEM_EXTRACTOR_MAIN_LOG_PATH))


class LLMExtractor(CacheOperations, AgentStatOperations):
    """Верхнеуровневый класс первой стадии Memorize-конвейера для извлечения информации (и её приведения в triplet-формат) из слабоструктурированных данных.

    :param agent: Коннектор к конкретному LLM-агенту для выполнения inference-операций.
    :type agent: AbstractAgentConnector
    :param config: Конфигурация Exctrator-стадии. Значение по умолчанию LLMExtractorConfig().
    :type config: LLMExtractorConfig, optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операциий в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    """

    def __init__(self, agent: AbstractAgentConnector, config: LLMExtractorConfig = LLMExtractorConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None) -> None:
        self.config = config

        if type(self.config.thesises_extraction_task_config) is str:
            thesises_extraction_version = self.config.thesises_extraction_task_config
            self.config.thesises_extraction_task_config = AgentThesisExtrTaskConfigSelector.select(
                base_config_version=thesises_extraction_version)
        
        if type(self.config.triplets_extraction_task_config) is str:
            triplets_extraction_version = self.config.triplets_extraction_task_config
            self.config.triplets_extraction_task_config = AgentTripletExtrTaskConfigSelector.select(
                base_config_version=triplets_extraction_version)

        self.agent = agent
        self.tasks_solvers: MemExtractorTaskSolvers = MemExtractorTaskSolvers(
            triplets_extraction_solver=AgentTaskSolver(
                self.agent, self.config.triplets_extraction_task_config,
                cache_kvdriver_config, inferencestat_config),
            thesises_extraction_solver=AgentTaskSolver(
                self.agent, self.config.thesises_extraction_task_config,
                cache_kvdriver_config, inferencestat_config)
        )

        self.log = self.config.log
        self.verbose = self.config.verbose

    def extract_knowledge(self, text: str, time: Union[None, str] = None, properties: Union[None, Dict] = None) -> Tuple[List[Triplet], ReturnInfo]:
        """Метод предназначен для извлечения информации (в виде триплетов) из слабоструктурированного текста на естественном языке.

        :param text: Слабоструктурированный текст.
        :type text: str
        :param properties: Набор свойств, который должен быть сохранён в памяти вмести с извлечённой из текста информацией, Значение по умолчанию None.
        :type properties: Union[None, Dict], optional
        :param time: Время, с которым ассоциированы события текста
        :type time: str, optional
        :return: Кортеж из двух объектов: (1) список извлечённой из текста информации (в виде триплетов); (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[List[Triplet], ReturnInfo]
        """
        assert self.config.need_simple or self.config.need_thesises
        props = dict() if properties is None else deepcopy(properties)

        assert 'time' not in props.keys()
        new_triplets, info = [], ReturnInfo()

        if time is not None:
            props["time"] = time

        self.log("START KNOWLEDGE EXTRACTION...", verbose=self.verbose)
        self.log(f"BASE_TEXT ID: {create_id(text)}", verbose=self.verbose)

        if self.config.need_simple:
            self.log("START SIMPLE-TRIPLETS EXTRACTION...",
                     verbose=self.verbose)
            tmp_triplets, status = self.tasks_solvers.triplets_extraction_solver.solve(
                lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy,
                text=text, rel_prop=props)
            self.log(f"STATUS: {STATUS_MESSAGE[status]}", verbose=self.verbose)

            if status != ReturnStatus.success:
                self.log(f"RESULT: None", verbose=self.verbose)
                info.occurred_warning.append(status)
            else:
                self.log(f"RESULT: {len(tmp_triplets)}", verbose=self.verbose)
                for triplet in tmp_triplets:
                    self.log(f"* {triplet}", verbose=self.verbose)
                new_triplets += tmp_triplets

        if self.config.need_thesises:
            self.log("START HYPER-TRIPLETS EXTRACTION...",
                     verbose=self.verbose)
            tmp_triplets, status = self.tasks_solvers.thesises_extraction_solver.solve(
                lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy,
                text=text, node_prop=props)
            self.log(f"STATUS: {STATUS_MESSAGE[status]}", verbose=self.verbose)

            if status != ReturnStatus.success:
                self.log(f"RESULT: None", verbose=self.verbose)
                info.occurred_warning.append(status)
            else:
                self.log(f"RESULT: {len(tmp_triplets)}", verbose=self.verbose)
                for triplet in tmp_triplets:
                    self.log(f"* {triplet}", verbose=self.verbose)
                new_triplets += tmp_triplets

        if self.config.need_episodic:
            self.log("START EPISODIC-TRIPLETS BUILDING...",
                     verbose=self.verbose)
            tmp_triplets = self.get_episodic_relationships(
                text, self.get_entities_from_triplets(new_triplets), node_prop=props)

            self.log(f"RESULT: {len(tmp_triplets)}", verbose=self.verbose)
            for triplet in tmp_triplets:
                self.log(f"* {triplet}", verbose=self.verbose)
            self.log(f"STATUS: {STATUS_MESSAGE[status]}", verbose=self.verbose)

            new_triplets += tmp_triplets

        if time is not None:
            self.log("ADDING TIME...", verbose=self.verbose)
            tmp_triplets = self.get_time_triplets(new_triplets, time)

            self.log(f"RESULT: {len(tmp_triplets)}", verbose=self.verbose)
            for triplet in tmp_triplets:
                self.log(f"* {triplet}", verbose=self.verbose)
            self.log(f"STATUS: {STATUS_MESSAGE[status]}", verbose=self.verbose)

            new_triplets += tmp_triplets

        if len(new_triplets) == 0:
            info.status = ReturnStatus.zero_triplets
            info.message = STATUS_MESSAGE[info.status]

        self.log(
            f"FINAL STATUS: {STATUS_MESSAGE[info.status]}", verbose=self.verbose)

        return new_triplets, info

    def get_entities_from_triplets(self, triplets: List[Triplet]) -> List[Node]:
        entities = {}
        for triplet in triplets:
            entities[triplet.start_node.stringified] = triplet.start_node
            entities[triplet.end_node.stringified] = triplet.end_node
        return list(entities.values())

    def get_episodic_relationships(self, text: str, entities: List[Node], node_prop: Dict = {}, rel_prop: Dict = {}) -> List[Triplet]:
        episodic_node = NodeCreator.create(
            name=text, n_type=NodeType.episodic, prop={**node_prop})
        episodic_rel = Relation(
            name=RelationType.episodic.value, type=RelationType.episodic, prop={**rel_prop})
        episodic_triplets = [TripletCreator.create(
            entity, episodic_rel, episodic_node) for entity in entities]
        return episodic_triplets

    def get_time_triplets(self, triplets: List[Triplet], time: str) -> List[Triplet]:
        time_node = NodeCreator.create(
            name=time, n_type=NodeType.time, prop={})
        time_rel = Relation(name=RelationType.time.value,
                            type=RelationType.time, prop={})
        start_nodes, picked_ids = [], set()
        for triplet in triplets:
            if (triplet.start_node.type == NodeType.episodic or triplet.start_node.type == NodeType.hyper) and triplet.start_node.id not in picked_ids:
                picked_ids.add(triplet.start_node.id)
                start_nodes.append(triplet.start_node)
            if (triplet.end_node.type == NodeType.episodic or triplet.end_node.type == NodeType.hyper) and triplet.end_node.id not in picked_ids:
                picked_ids.add(triplet.end_node.id)
                start_nodes.append(triplet.end_node)
        time_triplets = [TripletCreator.create(
            time_node, time_rel, node) for node in start_nodes]
        return time_triplets
