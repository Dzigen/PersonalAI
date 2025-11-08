from dataclasses import dataclass, field
from typing import List, Union, Dict
from copy import deepcopy

from .AStarTripletsRetriever import AStarGraphSearchConfig, AStarTripletsRetriever
from .WaterCirclesTripletsRetriever import WaterCirclesSearchConfig, WaterCirclesRetriever
from .NaiveBFSTripletsRetriever import NaiveBFSTripletsRetriever, NaiveBFSGraphSearchConfig
from .BeamSearchTripletsRetriever import BeamSearchTripletsRetriever, GraphBeamSearchConfig
from .NaiveTripletsRetriever import NaiveTripletsRetriever, NaiveGraphSearchConfig
from ..utils import AbstractTripletsRetriever, BaseGraphSearchConfig
from .......utils.data_structs import QueryInfo, Triplet, create_id, NodeType, NODES_TYPES_MAP
from .......kg_model import KnowledgeGraphModel
from .......utils import Logger
from .......utils.cache_kv import CacheUtils
from .......db_drivers.kv_driver import KeyValueDriverConfig


@dataclass
class MixturedGraphSearchConfig(BaseGraphSearchConfig):
    """Конфигурация смешанного алгоритма извлечения триплетов из графа знаний.

    :param retriever1_name: Наименование одного из алгоритмов (#1), который будет использоваться в комбинированном режиме для обхода вершин/рёбер графовой структуры данных (графа знаний) и извлечения релевантной информации. Значение по умолчанию 'astar'.
    :type retriever1_name: str, optional
    :param retriever1_config: Конфигурация выбранного алгоритма (#1) обхода графа. Значение по умолчанию AStarGraphSearchConfig().
    :type retriever1_config: Union[BaseGraphSearchConfig, Dict], optional
    :param retriever2_name: Наименование одного из алгоритмов (#2), который будет использоваться в комбинированном режиме для обхода вершин/рёбер графовой структуры данных (графа знаний) и извлечения релевантной информации. Значение по умолчанию 'watercircles'.
    :type retriever2_name: str, optional
    :param retriever2_config: Конфигурация выбранного алгоритма (#2) обхода графа. Значение по умолчанию WaterCirclesSearchConfig().
    :type retriever2_config: Union[BaseGraphSearchConfig, Dict], optional
    :param accepted_node_types: Типы вершин графа знаний, которые можно обходить в рамках запускаемых алгоритмов поиска/извелчения релевантной информации. Значение по умолчанию [NodeType.object, NodeType.hyper, NodeType.episodic, NodeType.time].
    :type accepted_node_types: List[NodeType], optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы NaiveBFSTripletsRetriever-класса. Значение по умолчанию 'qa_bfs_t_retriver_cache'.
    :type cache_table_name: str, optional
    """
    retriever1_name: str = 'astar'
    retriever1_config: Union[BaseGraphSearchConfig, Dict] = field(default_factory=lambda: AStarGraphSearchConfig())
    retriever2_name: str = 'watercircles'
    retriever2_config: Union[BaseGraphSearchConfig, Dict] = field(default_factory=lambda: WaterCirclesSearchConfig())
    accepted_node_types: List[Union[str, NodeType]] = field(default_factory=lambda: [NodeType.object, NodeType.hyper, NodeType.episodic, NodeType.time])
    cache_table_name: str = 'qa_mixture_t_retriever_cache'

    AVAILABLE_RCONFIGS: Dict[str, BaseGraphSearchConfig] = field(default_factory=lambda: {
        'astar': AStarGraphSearchConfig,
        'watercircles': WaterCirclesSearchConfig,
        'naive_bfs': NaiveBFSGraphSearchConfig,
        'beamsearch': GraphBeamSearchConfig,
        'naive_retriever': NaiveGraphSearchConfig
    })

    def to_str(self):
        retriever1_pair = (self.retriever1_name, self.retriever1_config.to_str())
        retriever2_pair = (self.retriever2_name, self.retriever2_config.to_str())
        sorted_pretr = sorted([retriever1_pair, retriever2_pair], key=lambda p: p[0])

        str_accepted_nodes = ";".join(sorted(list(map(lambda v: v.value, self.accepted_node_types))))
        return f"{sorted_pretr[0][0]};{sorted_pretr[0][1]};{sorted_pretr[1][0]};{sorted_pretr[1][1]};{str_accepted_nodes}"

    @staticmethod
    def from_dict(dict_config: Dict):
        formated_config = MixturedGraphSearchConfig(**dict_config)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self) -> None:
        for i, node_type in enumerate(self.accepted_node_types):
            if isinstance(node_type, str):
                self.accepted_node_types[i] = NODES_TYPES_MAP[node_type]

        if isinstance(self.retriever1_config, dict):
            self.retriever1_config = self.AVAILABLE_RCONFIGS[self.retriever1_name].from_dict(self.retriever1_config)
        else:
            self.retriever1_config.formate_fields()

        if isinstance(self.retriever2_config, dict):
            self.retriever2_config = self.AVAILABLE_RCONFIGS[self.retriever2_name].from_dict(self.retriever2_config)
        else:
            self.retriever2_config.formate_fields()


class MixturedTripletsRetriever(AbstractTripletsRetriever, CacheUtils):
    """Класс предназначен для извлечения триплетов из графа знаний на основе комбинации базовых алгоритмов обхода.

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты.
    :type log: Logger
    :param search_config: Конфигурация MixturedTripletsRetriever-алгоритма. Значение по умолчанию MixturedGraphSearchConfig().
    :type search_config: Union[MixturedGraphSearchConfig, Dict], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: Union[None,KeyValueDriverConfig], optional
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool, optional
    """
    AVAILABLE_RETRIEVERS: Dict[str, AbstractTripletsRetriever] = {
        'astar': AStarTripletsRetriever,
        'watercircles': WaterCirclesRetriever,
        'naive_bfs': NaiveBFSTripletsRetriever,
        'beamsearch': BeamSearchTripletsRetriever,
        'naive_retriever': NaiveTripletsRetriever
    }

    def __init__(self, kg_model: KnowledgeGraphModel, log: Logger, search_config: Union[MixturedGraphSearchConfig, Dict] = MixturedGraphSearchConfig(),
                 cache_kvdriver_config: KeyValueDriverConfig = None, verbose: bool = False) -> None:
        if isinstance(search_config, dict):
            search_config = MixturedGraphSearchConfig.from_dict(search_config)
        else:
            search_config.formate_fields()
        self.config: MixturedGraphSearchConfig = search_config

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, self.config.cache_table_name)

        self.retriever1: AbstractTripletsRetriever = self.AVAILABLE_RETRIEVERS[search_config.retriever1_name](
            kg_model, log, search_config.retriever1_config, cache_kvdriver_config, verbose)
        self.retriever2: AbstractTripletsRetriever = self.AVAILABLE_RETRIEVERS[search_config.retriever2_name](
            kg_model, log, search_config.retriever2_config, cache_kvdriver_config, verbose)

        # accepted nodes
        self.retriever1.config.accepted_node_types = search_config.accepted_node_types
        self.config.retriever1_config = self.retriever1.config
        self.retriever2.config.accepted_node_types = search_config.accepted_node_types
        self.config.retriever2_config = self.retriever2.config

        self.log = log
        self.verbose = verbose

    def clear_traversal_cache(self) -> None:
        self.retriever1.clear_traversal_cache()
        self.retriever2.clear_traversal_cache()

    def get_traversal_cache(self) -> Dict[str, Union[None, Dict, int]]:
        return {
            self.retriever1.__class__.__name__: self.retriever1.get_traversal_cache(),
            self.retriever2.__class__.__name__: self.retriever2.get_traversal_cache()
        }

    def get_cache_key(self, query_info: QueryInfo) -> List[str]:
        return [self.config.to_str(), query_info.to_str()]

    @CacheUtils.cache_method_output
    def get_relevant_triplets(self, query_info: QueryInfo) -> List[Triplet]:
        self.log("START KNOWLEDGE RETRIEVING ...", verbose=self.verbose)
        self.log(f"RETRIEVER: MixturedTripletsRetriever ({self.config.retriever1_name} + {self.config.retriever2_name})", verbose=self.verbose)
        self.log(f"BASE_QUESTION ID: {create_id(query_info.query)}", verbose=self.verbose)
        self.log(f"BASE_QUESTION: {query_info.query}", verbose=self.verbose)

        triplets1 = self.retriever1.get_relevant_triplets(query_info)
        triplets2 = self.retriever2.get_relevant_triplets(query_info)

        self.log(f"Количество триплетов, извлечённых с помощью {self.config.retriever1_name}/{self.config.retriever2_name}: {len(triplets1)}/{len(triplets2)}",
                 verbose=self.verbose)

        # отбираем только уникальные триплеты (по их идентификаторам)
        unique_triplets_map: Dict[str, Triplet] = dict()
        for triplet in triplets1 + triplets2:
            unique_triplets_map[triplet.relation.get_typedid()] = deepcopy(triplet)
        unique_triplets: List[Triplet] = list(unique_triplets_map.values())

        return unique_triplets
