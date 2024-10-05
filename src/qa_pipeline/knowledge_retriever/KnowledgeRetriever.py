from .utils import AbstractTriplesFilter, AbstractTripletsRetriever, LOG_PATH
from .TripletsFilter import TripletsFilterConfig, TripletsFilter
from .AStarTripletsRetriever import AStartTripletsRetriever, AStarGraphSearchConfig
from .cache import KeyValueStoreConfig, KeyValueStore
from ...utils.data_structs import QueryInfo, Triplet
from ...knowledge_graph_model import KnowledgeGraphModel
from ...utils import Logger

from dataclasses import dataclass, field
from typing import List

AVAILABLE_TRIPLETS_RETRIEVERS  = {
    'astar': AStartTripletsRetriever
}

AVAILABLE_TRIPLETS_FILTERS = {
    'naive': TripletsFilter
}

@dataclass
class KnowledgeRetrieverConfig:
    retriever_method: str = 'astar'
    retriever_config: object = field(default_factory=lambda: AStarGraphSearchConfig())
    filter_method: str = 'naive'
    filter_config: object = field(default_factory=lambda: TripletsFilterConfig())
    cache_config: KeyValueStoreConfig = field(default_factory=lambda: KeyValueStoreConfig())
    log: Logger = field(default_factory=lambda: Logger(LOG_PATH))
    verbose: bool = False

class KnowledgeRetriever:
    """Главный класс для извлечения релевантной информации из графа знаний
    по запросу пользователя 
    """
    def __init__(self, kg_model: KnowledgeGraphModel, config: KnowledgeRetrieverConfig = KnowledgeRetrieverConfig()) -> None:
        self.config = config
        self.kg_model = kg_model
        self.log = config.log
        self.cache = KeyValueStore(config.cache_config)

        self.graph_retriever = AVAILABLE_TRIPLETS_RETRIEVERS[self.config.retriever_method](
            kg_model, self.log, self.config.retriever_config, self.cache, self.config.verbose)
        
        self.triplets_filter = AVAILABLE_TRIPLETS_FILTERS[self.config.filter_method](
            kg_model, self.log, self.config.filter_config, self.config.verbose)

    def retrieve(self, query_info: QueryInfo) -> List[Triplet]:
        self.log("stage #3.1 - extracting triplets...", verbose=self.config.verbose)
        triplets = self.graph_retriever.get_relevant_triplets(query_info)
        self.log(f"Количество извлечённых триплетов: {len(triplets)}", verbose=self.config.verbose)

        self.log("stage #3.2 - filtering triplets...", verbose=self.config.verbose)
        filtered_triplets = self.triplets_filter.apply_filter(query_info, triplets)
        self.log(f"Количество триплетов после фильтрации: {len(filtered_triplets)}", verbose=self.config.verbose)

        return filtered_triplets