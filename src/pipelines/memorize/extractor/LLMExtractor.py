from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Union
from copy import deepcopy

from .config import MEM_EXTRACTOR_MAIN_LOG_PATH
from .utils import MemExtractorTaskSolvers, MemExtractorAgentTasksConfig
from ....utils import Logger, ReturnStatus, ReturnInfo, AgentTaskSolver, \
    accumulate_stage_info, accumulate_step_info, CompositeModuleDetailedResult, ModuleType
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

    :param agent_gen_stategy: Стратегия генерации текста для используемого LLM-агента. В случае None будет использоваться стратегия по умолчанию. Значение по умолчанию None.
    :type agent_gen_stategy: Union[None,Dict[str, Union[str, int, float]]], optional
    :param agent_tasks_config: Конфигурации LLM-промптов для решения заданных задач с помощью LLM-агента. Значение по умолчанию MemExtractorAgentTasksConfig().
    :type agent_tasks_config: Union[Dict, MemExtractorAgentTasksConfig], optional
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

    log_path: str = MEM_EXTRACTOR_MAIN_LOG_PATH

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
    :param config: Конфигурация Exctraсtor-стадии. Значение по умолчанию LLMExtractorConfig().
    :type config: Union[Dict, LLMExtractorConfig], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операций в рамках LLM-задач. Значение по умолчанию None.
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
        self.config.agent_tasks_config.versions_to_configs(
            self.config.verbose, self.config.log_level)

        self.agent = agent
        self.tasks_solvers: MemExtractorTaskSolvers = MemExtractorTaskSolvers(
            triplets_extraction_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.triplets_extraction,
                cache_kvdriver_config, inferencestat_config),
            thesises_extraction_solver=AgentTaskSolver(
                self.agent, self.config.agent_tasks_config.thesises_extraction,
                cache_kvdriver_config, inferencestat_config)
        )

        self.log = Logger(config.log_path)
        self.verbose = self.config.verbose
        self.log_level = self.config.log_level

    @accumulate_stage_info
    def extract_knowledge(self, text: str, time: Union[None, str] = None, properties: Union[None, Dict] = None) -> Tuple[List[Triplet], ReturnInfo, CompositeModuleDetailedResult, bool]:
        """Метод предназначен для извлечения информации (в виде триплетов) из слабоструктурированного текста на естественном языке.

        :param text: Слабоструктурированный текст.
        :type text: str
        :param properties: Набор свойств, который должен быть сохранён в памяти вместе с извлечённой из текста информацией. Значение по умолчанию None.
        :type properties: Union[None, Dict], optional
        :param time: Время, с которым ассоциированы события текста.
        :type time: str, optional
        :return: Кортеж из четырёх объектов: (1) список извлечённой из текста информации (в виде триплетов); (2) статус завершения операции с пояснительной информацией; (3) структура данных с промежуточными результатами реботы метода; (4) True, если результат был получен из кеша (cache hit), иначе False.
        :rtype: Tuple[List[Triplet], ReturnInfo, CompositeModuleDetailedResult, bool]
        """
        assert self.config.need_simple or self.config.need_thesises
        props = dict() if properties is None else deepcopy(properties)

        assert 'time' not in props.keys()
        new_triplets, rinfo = [], ReturnInfo()
        module_trace = CompositeModuleDetailedResult()

        if time is not None:
            props["time"] = time

        self.log.debug("START KNOWLEDGE EXTRACTION...", verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* text hash: %s", create_id(text), verbose=self.verbose, log_level=self.log_level)

        if self.config.need_simple:
            self.log.debug("START SIMPLE-TRIPLETS EXTRACTION...", verbose=self.verbose, log_level=self.log_level)
            tmp_triplets, status, trace = self.tasks_solvers.triplets_extraction_solver.solve(
                lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, text=text, rel_prop=props)
            self.log.debug("STATUS: %s .", STATUS_MESSAGE[status], verbose=self.verbose, log_level=self.log_level)
            module_trace.add('triplets_extraction_solver', ModuleType.task_solver, trace)

            if status != ReturnStatus.success:
                self.log.warning("RESULT: None", verbose=self.verbose, log_level=self.log_level)
                rinfo.occurred_warning.append(status)
            else:
                self.log.debug("RESULT: %d", len(tmp_triplets), verbose=self.verbose, log_level=self.log_level)
                for triplet in tmp_triplets:
                    self.log.debug("* %s", triplet, verbose=self.verbose, log_level=self.log_level)
                new_triplets += tmp_triplets

        if self.config.need_thesises:
            self.log.debug("START HYPER-TRIPLETS EXTRACTION...", verbose=self.verbose, log_level=self.log_level)
            tmp_triplets, status, trace = self.tasks_solvers.thesises_extraction_solver.solve(
                lang=self.config.lang, gen_strategy=self.config.agent_gen_stategy, text=text, node_prop=props)
            self.log.debug("STATUS: %s .", STATUS_MESSAGE[status], verbose=self.verbose, log_level=self.log_level)
            module_trace.add('thesises_extraction_solver', ModuleType.task_solver, trace)

            if status != ReturnStatus.success:
                self.log.debug("RESULT: None", verbose=self.verbose, log_level=self.log_level)
                rinfo.occurred_warning.append(status)
            else:
                self.log.debug("RESULT: %d", len(tmp_triplets), verbose=self.verbose, log_level=self.log_level)
                for triplet in tmp_triplets:
                    self.log.debug("* %s", triplet, verbose=self.verbose, log_level=self.log_level)
                new_triplets += tmp_triplets

        if self.config.need_episodic:
            self.log.debug("START EPISODIC-TRIPLETS BUILDING...", verbose=self.verbose, log_level=self.log_level)
            tmp_triplets, _, trace = self.get_episodic_relationships(
                text, self.get_entities_from_triplets(new_triplets), node_prop=props)
            self.log.debug("STATUS: %s", STATUS_MESSAGE[status], verbose=self.verbose, log_level=self.log_level)
            module_trace.add('get_entities_from_triplets', ModuleType.step, trace)

            self.log.debug("RESULT: %d", len(tmp_triplets), verbose=self.verbose, log_level=self.log_level)
            for triplet in tmp_triplets:
                self.log.debug("* %s", triplet, verbose=self.verbose, log_level=self.log_level)

            new_triplets += tmp_triplets

        if time is not None:
            self.log.debug("ADDING TIME...", verbose=self.verbose, log_level=self.log_level)
            tmp_triplets, _, trace = self.get_time_triplets(new_triplets, time)
            self.log.debug("STATUS: %s .", STATUS_MESSAGE[status], verbose=self.verbose, log_level=self.log_level)
            module_trace.add('get_time_triplets', ModuleType.step, trace)

            self.log.debug("RESULT: %d ", len(tmp_triplets), verbose=self.verbose, log_level=self.log_level)
            for triplet in tmp_triplets:
                self.log.debug("* %s ", triplet, verbose=self.verbose, log_level=self.log_level)

            new_triplets += tmp_triplets

        if len(new_triplets) == 0:
            rinfo.status = ReturnStatus.zero_triplets
            rinfo.message = STATUS_MESSAGE[rinfo.status]

        self.log.debug("FINAL STATUS: %s", STATUS_MESSAGE[rinfo.status], verbose=self.verbose, log_level=self.log_level)

        return new_triplets, rinfo, module_trace, False

    def get_entities_from_triplets(self, triplets: List[Triplet]) -> List[Node]:
        entities = {}
        for triplet in triplets:
            entities[triplet.start_node.stringified] = triplet.start_node
            entities[triplet.end_node.stringified] = triplet.end_node
        return list(entities.values())

    @accumulate_step_info
    def get_episodic_relationships(self, text: str, entities: List[Node], node_prop: Union[None, Dict] = None, rel_prop: Union[None, Dict] = None) -> Tuple[List[Triplet], ReturnInfo, bool]:
        rinfo = ReturnInfo()
        episodic_node = NodeCreator.create(name=text, n_type=NodeType.episodic, prop=dict() if node_prop is None else node_prop)
        episodic_rel = Relation(name=RelationType.episodic.value, type=RelationType.episodic, prop=dict() if rel_prop is None else rel_prop)
        episodic_triplets = [TripletCreator.create(entity, episodic_rel, episodic_node) for entity in entities]
        return episodic_triplets, rinfo, False

    @accumulate_step_info
    def get_time_triplets(self, triplets: List[Triplet], time: str) -> Tuple[List[Triplet], ReturnInfo, bool]:
        rinfo = ReturnInfo()
        time_node = NodeCreator.create(name=time, n_type=NodeType.time, prop={})
        time_rel = Relation(name=RelationType.time.value, type=RelationType.time, prop={})
        start_nodes, picked_ids = [], set()
        for triplet in triplets:
            if (triplet.start_node.type == NodeType.episodic or triplet.start_node.type == NodeType.hyper) and triplet.start_node.id not in picked_ids:
                picked_ids.add(triplet.start_node.id)
                start_nodes.append(triplet.start_node)
            if (triplet.end_node.type == NodeType.episodic or triplet.end_node.type == NodeType.hyper) and triplet.end_node.id not in picked_ids:
                picked_ids.add(triplet.end_node.id)
                start_nodes.append(triplet.end_node)
        time_triplets = [TripletCreator.create(time_node, time_rel, node) for node in start_nodes]
        return time_triplets, rinfo, False
