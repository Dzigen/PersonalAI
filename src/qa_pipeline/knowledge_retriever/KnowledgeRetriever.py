from .utils import KnowledgeRetrieverConfig
from ..query_parser.utils import QueryInfo
from ...knowledge_graph_model import KnowledgeGraphModel

class KnowledgeRetriever:
    def __init__(self, config: KnowledgeRetrieverConfig, kg_model: KnowledgeGraphModel) -> None:
        self.config = config
        self.kg_model = kg_model

    def retrieve(self, query: QueryInfo):
        pass

    def retrieve_triplets(self):
        pass