from dataclasses import dataclass, field
from typing import List, Union, Dict, Tuple
from copy import deepcopy

from .configs import MIXTURED_RETRIEVER_LOG_PATH
from .AStarTripletsRetriever import AStarGraphSearchConfig, AStarTripletsRetriever
from .WaterCirclesTripletsRetriever import WaterCirclesSearchConfig, WaterCirclesRetriever
from .NaiveBFSTripletsRetriever import NaiveBFSTripletsRetriever, NaiveBFSGraphSearchConfig
from .BeamSearchTripletsRetriever import BeamSearchTripletsRetriever, GraphBeamSearchConfig
from .NaiveTripletsRetriever import NaiveTripletsRetriever, NaiveGraphSearchConfig
from ..utils import AbstractTripletsRetriever, BaseGraphSearchConfig
from .......utils.data_structs import QueryInfo, Triplet, create_id, NodeType, NODES_TYPES_MAP
from .......kg_model import KnowledgeGraphModel
from .......utils import Logger, accumulate_step_info, ReturnInfo
from .......utils.cache_kv import CacheUtils
from .......db_drivers.kv_driver import KeyValueDriverConfig


@dataclass
class MixturedGraphSearchConfig(BaseGraphSearchConfig):
    """Конфигурация смешанного алгоритма извлечения триплетов из графа знаний.

    :param retriever1_name: Наименование одного из алгоритмов (#1), который будет использоваться в комбинированном режиме для обхода вершин/рёбер графовой структуры данных (графа знаний) и извлечения релевантной информации. Значение по умолчанию 'beamsearch'.
    :type retriever1_name: str, optional
    :param retriever1_config: Конфигурация выбранного алгоритма (#1) обхода графа. Значение по умолчанию GraphBeamSearchConfig().
    :type retriever1_config: Union[BaseGraphSearchConfig, Dict], optional
    :param retriever2_name: Наименование одного из алгоритмов (#2), который будет использоваться в комбинированном режиме для обхода вершин/рёбер графовой структуры данных (графа знаний) и извлечения релевантной информации. Значение по умолчанию 'watercircles'.
    :type retriever2_name: str, optional
    :param retriever2_config: Конфигурация выбранного алгоритма (#2) обхода графа. Значение по умолчанию WaterCirclesSearchConfig().
    :type retriever2_config: Union[BaseGraphSearchConfig, Dict], optional
    :param accepted_node_types: Типы вершин графа знаний, которые можно обходить в рамках запускаемых алгоритмов поиска/извлечения релевантной информации. Значение по умолчанию [NodeType.object, NodeType.hyper, NodeType.episodic].
    :type accepted_node_types: List[Union[str, NodeType]], optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы NaiveBFSTripletsRetriever-класса. Значение по умолчанию 'qa_bfs_t_retriver_cache'.
    :type cache_table_name: str, optional
    """
    retriever1_name: str = 'beamsearch'
    retriever1_config: Union[BaseGraphSearchConfig, Dict] = field(default_factory=lambda: GraphBeamSearchConfig())
    retriever2_name: str = 'watercircles'
    retriever2_config: Union[BaseGraphSearchConfig, Dict] = field(default_factory=lambda: WaterCirclesSearchConfig())
    accepted_node_types: List[Union[str, NodeType]] = field(default_factory=lambda: [NodeType.object, NodeType.hyper, NodeType.episodic])  # NodeType.time
    cache_table_name: str = 'qa_mixture_t_retriever_cache'
    log_path: str = MIXTURED_RETRIEVER_LOG_PATH

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
        dictconfig_copy = deepcopy(dict_config)
        formated_config = MixturedGraphSearchConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self) -> None:
        for i, node_type in enumerate(self.accepted_node_types):
            if not isinstance(node_type, NodeType):
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
    :param search_config: Конфигурация MixturedTripletsRetriever-алгоритма. Значение по умолчанию MixturedGraphSearchConfig().
    :type search_config: Union[MixturedGraphSearchConfig, Dict], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: Union[None, KeyValueDriverConfig], optional
    """
    AVAILABLE_RETRIEVERS: Dict[str, AbstractTripletsRetriever] = {
        'astar': AStarTripletsRetriever,
        'watercircles': WaterCirclesRetriever,
        'naive_bfs': NaiveBFSTripletsRetriever,
        'beamsearch': BeamSearchTripletsRetriever,
        'naive_retriever': NaiveTripletsRetriever
    }

    def __init__(self, kg_model: KnowledgeGraphModel, search_config: Union[MixturedGraphSearchConfig, Dict] = MixturedGraphSearchConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None) -> None:
        if isinstance(search_config, dict):
            search_config = MixturedGraphSearchConfig.from_dict(search_config)
        else:
            search_config.formate_fields()
        self.config: MixturedGraphSearchConfig = search_config

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, self.config.cache_table_name)

        # accepted nodes
        self.config.retriever1_config.accepted_node_types = self.config.accepted_node_types
        self.config.retriever2_config.accepted_node_types = self.config.accepted_node_types

        self.retriever1: AbstractTripletsRetriever = self.AVAILABLE_RETRIEVERS[search_config.retriever1_name](
            kg_model, self.config.retriever1_config, cache_kvdriver_config)
        self.retriever2: AbstractTripletsRetriever = self.AVAILABLE_RETRIEVERS[search_config.retriever2_name](
            kg_model, self.config.retriever2_config, cache_kvdriver_config)

        self.log = Logger(search_config.log_path)
        self.verbose = search_config.verbose
        self.log_level = search_config.log_level

    def close_connections(self):
        if self.cachekv is not None:
            self.cachekv.close_connection()
        self.retriever1.close_connections()
        self.retriever2.close_connections()

    def clear_traversal_cache(self) -> None:
        self.retriever1.clear_kv_caches(
            clear_retrieval_cache=True, clear_traversal_cache=True)
        self.retriever2.clear_kv_caches(
            clear_retrieval_cache=True, clear_traversal_cache=True
        )

    def get_traversal_cache(self) -> Dict[str, Union[None, Dict, int]]:
        return {
            self.retriever1.__class__.__name__: self.retriever1.get_cache_stat(get_traversal_cache=True),
            self.retriever2.__class__.__name__: self.retriever2.get_cache_stat(get_traversal_cache=True)
        }

    def get_cache_key(self, query_info: QueryInfo) -> List[str]:
        return [self.config.to_str(), query_info.to_str()]

    @accumulate_step_info
    @CacheUtils.cache_method_output
    def get_relevant_triplets(self, query_info: QueryInfo) -> Tuple[List[Triplet], ReturnInfo]:
        self.log.debug("START KNOWLEDGE RETRIEVING ...", verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Retriever: MixturedTripletsRetriever (%s + %s)", self.config.retriever1_name, self.config.retriever2_name,
                       verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Question hash: %s", create_id(query_info.query), verbose=self.verbose, log_level=self.log_level)
        self.log.debug("* Question: %s", query_info.query, verbose=self.verbose, log_level=self.log_level)
        rinfo = ReturnInfo()
        triplets1, _, _ = self.retriever1.get_relevant_triplets(query_info)
        triplets2, _, _ = self.retriever2.get_relevant_triplets(query_info)

        self.log.debug(f"Количество триплетов, извлечённых с помощью %s/%s: %d/%d",
                       self.config.retriever1_name, self.config.retriever2_name, len(triplets1), len(triplets2),
                       verbose=self.verbose, log_level=self.log_level)

        # отбираем только уникальные триплеты (по их идентификаторам)
        unique_triplets_map: Dict[str, Triplet] = dict()
        for triplet in triplets1 + triplets2:
            unique_triplets_map[triplet.relation.get_typedid()] = deepcopy(triplet)
        unique_triplets: List[Triplet] = list(unique_triplets_map.values())

        return unique_triplets, rinfo
