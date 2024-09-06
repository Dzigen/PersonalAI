from .utils import KnowledgeRetrieverConfig
from ..query_parser.utils import QueryInfo
from ...knowledge_graph_model import KnowledgeGraphModel

class KnowledgeRetriever:
    def __init__(self, config: KnowledgeRetrieverConfig, kg_model: KnowledgeGraphModel) -> None:
        self.config = config
        self.kg_model = kg_model

        self.graph_retriever = self.config.graph_search_method(
            kg_model, self.config.graph_search_config)
        self.triplets_filter = self.config.triplets_filter_method(
            kg_model, self.config.triplets_filter_config)

    def retrieve(self, query_info: QueryInfo):
        raw_triplets = self.graph_retriever.get_relevant_triplets(query_info)
        