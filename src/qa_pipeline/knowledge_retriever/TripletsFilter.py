from ...knowledge_graph_model import KnowledgeGraphModel
from ..query_parser.utils import QueryInfo
from ...embedding_functions import VectorDBInstance
from .utils import AbstractTriplesFilter, Triplet

from dataclasses import dataclass
from typing import List

@dataclass
class TripletsFilterConfig:
    max_k: int = 100

class TripletsFilter(AbstractTriplesFilter):
    """Главный класс для фильтрации триплетов, извлечённых из графа знаний, 
    на основе их релевантности пользовательскому запросу.
    """

    def __init__(self, kg_model: KnowledgeGraphModel, config: TripletsFilterConfig) -> None:
        self.kg_model = kg_model
        self.config = config

    def apply_filter(self, query_info: QueryInfo, triplets: List[Triplet]) -> List[Triplet]:

        filtered_triplets = []
        query_embd = self.kg_model.embeddings_db.embedder.encode_queries([query_info.query])[0]
        query_instance = VectorDBInstance(embedding=query_embd)
        base_triplets_ids = list(map(lambda triplet: triplet.id, triplets))

        if len(base_triplets_ids) > 0:
            raw_relevant_triplets = self.kg_model.embeddings_db['triplets'].retrieve(
                [query_instance], self.config.max_k, where={"triplet_id": {"$in": base_triplets_ids}})[0]
            accepted_tripletes_ids = list(map(lambda item: item[1]['id'], raw_relevant_triplets))
            filtered_triplets = list(filter(lambda triplet: triplet.relation.id in accepted_tripletes_ids, triplets))

        return filtered_triplets   
            
        
