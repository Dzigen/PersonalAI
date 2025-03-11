from dataclasses import dataclass, field
from typing import List, Union, Dict
from copy import deepcopy

from .utils import AbstractTripletsRetriever, BaseGraphSearchConfig
from .AStarTripletsRetriever import AStarGraphSearchConfig, AStarTripletsRetriever
from .WaterCirclesTripletsRetriever import WaterCirclesSearchConfig, WaterCirclesRetriever
from .NaiveBFSTripletsRetriever import NaiveBFSTripletsRetriever
from .BeamSearchTripletsRetriever import BeamSearchTripletsRetriever
from ......utils.data_structs import QueryInfo, Triplet, create_id, NodeType
from ......kg_model import KnowledgeGraphModel
from ......utils import Logger
from ......utils.cache_kv import CacheKV, CacheUtils
from ......db_drivers.kv_driver import KeyValueDriverConfig, KVDBConnectionConfig

@dataclass
class MixturedGraphSearchConfig(BaseGraphSearchConfig):
    """Конфигурация комбинированного алгоритма извлечения триплетов из графа знаний.

    :param astar_config: Конфигурация A*-алгоритма поиска. Значение по умолчанию AStarGraphSearchConfig().
    :type astar_config: AStarGraphSearchConfig
    :param bfs_config: Конфигурация BFS-алгоритма поиска. Значение по умолчанию BFSSearchConfig().
    :type bfs_config: BFSSearchConfig
    """
    retriever1_name: str = 'astar'
    retriever1_config: Union[BaseGraphSearchConfig, Dict] = field(default_factory=lambda: AStarGraphSearchConfig())
    retriever2_name: str = 'watercircles'
    retriever2_config: Union[BaseGraphSearchConfig, Dict] = field(default_factory=lambda: WaterCirclesSearchConfig())
    accepted_node_types: List[NodeType] = field(default_factory=lambda:[NodeType.object, NodeType.hyper, NodeType.episodic, NodeType.time])
    cache_table_name: str = 'qa_mixture_t_retriever_cache'

class MixturedTripletsRetriever(AbstractTripletsRetriever, CacheUtils):
    """Класс предназначен для извлечения триплетов из графа знаний с помощью комбинации BFS- и A*-алгоритмов поиска.

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param config: Конфигурация комбинированного алгоритма поиска. Значение по умолчанию MixturedGraphSearchConfig().
    :type config: MixturedGraphSearchConfig
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты. Значение по умолчанию Logger(LOG_PATH).
    :type log: Logger
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool
    """
    def __init__(self, kg_model: KnowledgeGraphModel, log: Logger, search_config: Union[MixturedGraphSearchConfig, Dict] = MixturedGraphSearchConfig(),
                 cache_kvdriver_config: KeyValueDriverConfig = None, verbose: bool = False) -> None:
        self.log = log
        self.verbose = verbose

        if type(search_config) is dict:
            search_config = MixturedGraphSearchConfig(**search_config)
        self.config = search_config

        self.available_retrievers = {
            'astar': AStarTripletsRetriever,
            'watercircles': WaterCirclesRetriever,
            'naive_bfs': NaiveBFSTripletsRetriever,
            'beamsearch': BeamSearchTripletsRetriever
        }

        # accepted nodes
        search_config.retriever1_config.accepted_node_types = search_config.accepted_node_types
        search_config.retriever2_config.accepted_node_types = search_config.accepted_node_types

        self.retriever1 = self.available_retrievers[search_config.retriever1_name](
            kg_model, log, search_config.retriever1_config, cache_kvdriver_config, verbose)
        self.retriever2 = self.available_retrievers[search_config.retriever2_name](
            kg_model, log, search_config.retriever2_config, cache_kvdriver_config, verbose)

        if cache_kvdriver_config is not None and self.config.cache_table_name is not None:
            cache_config = deepcopy(cache_kvdriver_config)
            cache_config.db_config.db_info['table'] = self.config.cache_table_name
            self.cachekv = CacheKV(cache_config)
        else:
            self.cachekv = None

    def get_cache_key(self, query_info: QueryInfo) -> List[object]:
        return [self.config.retriever1_name] + self.retriever1.get_cache_key(query_info) + \
            [self.config.retriever2_name] + self.retriever2.get_cache_key(query_info) + [query_info]

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
        unique_triplets = dict()
        for triplet in triplets1 + triplets2:
            unique_triplets[triplet.id] = deepcopy(triplet)

        return list(unique_triplets.values())
