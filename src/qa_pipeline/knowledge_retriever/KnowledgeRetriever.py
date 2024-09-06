from .utils import KnowledgeRetrieverConfig
from ..query_parser.utils import QueryInfo
from ...knowledge_graph_model import KnowledgeGraphModel
from ..knowledge_retriever.utils import Triplet

from typing import List

class KnowledgeRetriever:
    def __init__(self, config: KnowledgeRetrieverConfig, kg_model: KnowledgeGraphModel) -> None:
        self.config = config
        self.kg_model = kg_model

        self.graph_retriever = self.config.graph_search_method(
            kg_model, self.config.graph_search_config)
        self.triplets_filter = self.config.triplets_filter_method(
            kg_model, self.config.triplets_filter_config)

    def retrieve(self, query_info: QueryInfo) -> List[Triplet]:
        triplets = self.graph_retriever.get_relevant_triplets(query_info)
        filtered_triplets = self.triplets_filter.apply_filter(query_info, triplets)
        return filtered_triplets