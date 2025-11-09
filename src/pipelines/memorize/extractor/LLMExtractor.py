from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Union
from copy import deepcopy

from .config import MEM_EXTRACTOR_MAIN_LOG_PATH
from .utils import MemExtractorTaskSolvers, MemExtractorAgentTasksConfig
from ....utils import Logger, ReturnStatus, ReturnInfo, AgentTaskSolver
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
    :param agent_tasks_config: Конфигурации LLM-промптом для решения заданных задач с помощью LLM-агента. Значение по умолчанию MemExtractorAgentTasksConfig().
    :type agent_tasks_config: Union[Dict,MemExtractorAgentTasksConfig], optional
    :param need_simple: Если True, то из входного текста на первой стадии Mem-конвейера будет выполнено извлечение триплетов с типом связи 'simple', иначе False. Значение по умолчанию True.
    :type need_simple: bool, optional
    :param need_thesises: Если True, то из входного текста на первой стадии Mem-конвейера будет выполнено извлечение триплетов с типом связи 'hyper', иначе False. Значение по умолчанию True.
    :type need_thesises: bool, optional
    :param need_episodic: Если True, то из входного текста на первой стадии Mem-конвейера будет выполнено извлечение триплетов с типом связи 'episodic', иначе False. Значение по умолчанию True.
    :type need_episodic: bool, optional
    """
    agent_gen_stategy: Union[None, Dict[str, Union[str, int, float]]] = None
    agent_tasks_config: Union[Dict, MemExtractorAgentTasksConfig] = field(default_factory=lambda: MemExtractorAgentTasksConfig())
    need_simple: bool = True
    need_thesises: bool = True
    need_episodic: bool = True

    log: Logger = field(default_factory=lambda: Logger(MEM_EXTRACTOR_MAIN_LOG_PATH))

    def to_str(self):
        # TODO
        raise NotImplementedError

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = LLMExtractorConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.agent_tasks_config, dict):
            self.agent_tasks_config = MemExtractorAgentTasksConfig.from_dict(self.agent_tasks_config)
        else:
            self.agent_tasks_config.formate_fields()


class LLMExtractor(CacheOperations, AgentStatOperations):
    """Верхнеуровневый класс первой стадии Memorize-конвейера для извлечения информации (и её приведения в triplet-формат) из слабоструктурированных данных.

    :param agent: Коннектор к конкретному LLM-агенту для выполнения inference-операций.
    :type agent: AbstractAgentConnector
    :param config: Конфигурация Exctrator-стадии. Значение по умолчанию LLMExtractorConfig().
    :type config: Union[Dict,LLMExtractorConfig], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операциий в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    """

    def __init__(self, agent: AbstractAgentConnector, config: Union[Dict, LLMExtractorConfig] = LLMExtractorConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None) -> None:
        if isinstance(config, dict):
            config: LLMExtractorConfig = LLMExtractorConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config = config
        self.config.agent_tasks_config.versions_to_configs()

        self.agent = agent
        self.tasks_solvers: MemExtractorTaskSolvers = MemExtractorTaskSolvers(
            triplets_extraction_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.triplets_extraction,
                cache_kvdriver_config, inferencestat_config),
            thesises_extraction_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.thesises_extraction,
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
