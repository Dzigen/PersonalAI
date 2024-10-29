from .utils import AbstractTriplesFilter, AbstractTripletsRetriever, RETRIEVER_LOG_PATH
from .TripletsFilter import TripletsFilterConfig, TripletsFilter
from .AStarTripletsRetriever import AStarTripletsRetriever, AStarGraphSearchConfig
from .BFSTripletsRetriever import BFSRetriever, BFSSearchConfig
from .MixturedTripletsRetriever import MixturedTripletsRetriever, MixturedGraphSearchConfig
from ...utils.data_structs import QueryInfo, Triplet
from ...knowledge_graph_model import KnowledgeGraphModel
from ...db_drivers.kv_driver import KeyValueDriver, KeyValueDriverConfig
from ...utils import Logger, ReturnStatus, ReturnInfo
from ...utils.errors import QA_ZERO_RETRIEVED_TRIPLETS_MSG

from dataclasses import dataclass, field
from typing import List, Tuple

#
AVAILABLE_TRIPLETS_RETRIEVERS  = {
    'astar': AStarTripletsRetriever,
    'bfs': BFSRetriever,
    'mixture': MixturedTripletsRetriever
}

#
AVAILABLE_TRIPLETS_FILTERS = {
    'naive': TripletsFilter
}

@dataclass
class KnowledgeRetrieverConfig:
    """_summary_
    """
    #
    retriever_method: str = 'astar'
    #
    retriever_config: object = field(default_factory=lambda: AStarGraphSearchConfig())
    #
    filter_method: str = 'naive'
    #
    filter_config: object = field(default_factory=lambda: TripletsFilterConfig())
    #
    cache_config: KeyValueDriverConfig = field(default_factory=lambda: KeyValueDriverConfig())
    #
    log: Logger = field(default_factory=lambda: Logger(RETRIEVER_LOG_PATH))
    verbose: bool = False

class KnowledgeRetriever:
    """Главный класс для извлечения релевантной информации из графа знаний
    по запросу пользователя
    """
    def __init__(self, kg_model: KnowledgeGraphModel, config: KnowledgeRetrieverConfig = KnowledgeRetrieverConfig()) -> None:
        """_summary_

        :param kg_model: _description_
        :type kg_model: KnowledgeGraphModel
        :param config: _description_, defaults to KnowledgeRetrieverConfig()
        :type config: KnowledgeRetrieverConfig, optional
        """
        self.config = config
        self.kg_model = kg_model
        self.log = config.log
        self.cache = KeyValueDriver.connect(config.cache_config)

        self.graph_retriever = AVAILABLE_TRIPLETS_RETRIEVERS[self.config.retriever_method](
            kg_model, self.log, self.config.retriever_config, self.cache, self.config.verbose)

        self.triplets_filter = AVAILABLE_TRIPLETS_FILTERS[self.config.filter_method](
            kg_model, self.log, self.config.filter_config, self.config.verbose)

    def retrieve(self, query_info: QueryInfo) -> Tuple[List[Triplet], ReturnInfo]:
        """_summary_

        :param query_info: _description_
        :type query_info: QueryInfo
        :return: _description_
        :rtype: Tuple[List[Triplet], ReturnInfo]
        """
        info = ReturnInfo()
        self.log("stage #3.1 - extracting triplets...", verbose=self.config.verbose)
        triplets = self.graph_retriever.get_relevant_triplets(query_info)
        self.log(f"Количество извлечённых триплетов: {len(triplets)}", verbose=self.config.verbose)

        self.log("stage #3.2 - filtering triplets...", verbose=self.config.verbose)
        filtered_triplets = self.triplets_filter.apply_filter(query_info, triplets)
        self.log(f"Количество триплетов после фильтрации: {len(filtered_triplets)}", verbose=self.config.verbose)

        if len(filtered_triplets) == 0:
            info.status = ReturnStatus.zero_retrieved_triplets
            info.message = QA_ZERO_RETRIEVED_TRIPLETS_MSG

        return filtered_triplets, info
