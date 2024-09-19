from .utils import AbstractTriplesFilter, AbstractTripletsRetriever
from .TripletsFilter import TripletsFilterConfig, TripletsFilter
from .AStarTripletsRetriever import AStartTripletsRetriever, AStarGraphSearchConfig
from ...utils.data_structs import QueryInfo, Triplet
from ...knowledge_graph_model import KnowledgeGraphModel

from dataclasses import dataclass, field
from typing import List

@dataclass
class KnowledgeRetrieverConfig:
    graph_retriever_method: AbstractTripletsRetriever = field(default_factory=lambda: AStartTripletsRetriever)
    graph_retriever_config: object = field(default_factory=lambda: AStarGraphSearchConfig())
    triplets_filter_method: AbstractTriplesFilter = field(default_factory=lambda: TripletsFilter)
    triplets_filter_config: object = field(default_factory=lambda: TripletsFilterConfig())

class KnowledgeRetriever:
    """Главный класс для извлечения релевантной информации из графа знаний
    по запросу пользователя 
    """
    def __init__(self, kg_model: KnowledgeGraphModel, config: KnowledgeRetrieverConfig = KnowledgeRetrieverConfig()) -> None:
        self.config = config
        self.kg_model = kg_model

        self.graph_retriever = self.config.graph_retriever_method(
            kg_model, self.config.graph_retriever_config)
        
        # TODO
        # реализовать дополнительный этап для фильтрации по содержанию

        self.triplets_filter = self.config.triplets_filter_method(
            kg_model, self.config.triplets_filter_config)

    def retrieve(self, query_info: QueryInfo) -> List[Triplet]:
        triplets = self.graph_retriever.get_relevant_triplets(query_info)
        filtered_triplets = self.triplets_filter.apply_filter(query_info, triplets)
        return filtered_triplets