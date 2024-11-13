from dataclasses import dataclass
from typing import List

from .utils import AbstractTriplesFilter, BaseTripletsFilterConfig
from ...utils.data_structs import Triplet, QueryInfo
from ...utils import Logger
from ...knowledge_graph_model import KnowledgeGraphModel
from ...db_drivers.vector_driver import VectorDBInstance

@dataclass
class TripletsFilterConfig(BaseTripletsFilterConfig):
    #: Первые k (по релевантности) триплетов, которые будут возвращены в результате операции ранжирования.
    max_k: int = 50

class TripletsFilter(AbstractTriplesFilter):
    """Класс предназначен для ранжирования/фильтрации триплетов, извлечённых из графа знаний,
    на основе их релевантности к user-вопросу.
    """

    def __init__(self, kg_model: KnowledgeGraphModel, log: Logger, config: TripletsFilterConfig, log_verbose: bool = False) -> None:
        self.log = log
        self.log_verbose = log_verbose
        self.kg_model = kg_model
        self.config = config

    def apply_filter(self, query_info: QueryInfo, triplets: List[Triplet]) -> List[Triplet]:
        filtered_triplets = []
        query_embd = self.kg_model.embeddings_struct.embedder.encode_queries([query_info.query])[0]
        query_instance = VectorDBInstance(embedding=query_embd)
        base_relation_ids = list(map(lambda triplet: triplet.relation.id, triplets))

        self.log(f"Количество уникальных триплетов: {len(set(base_relation_ids))}", verbose=self.log_verbose)

        if len(base_relation_ids) > 0:
            raw_relevant_triplets = self.kg_model.embeddings_struct.vectordbs['triplets'].retrieve(
                [query_instance], self.config.max_k, includes=['embeddings', 'documents', 'metadatas'], where={"id": {"$in": base_relation_ids}})[0]
            accepted_tripletes_ids = list(map(lambda item: item[1].id, raw_relevant_triplets))
            filtered_triplets = list(filter(lambda triplet: triplet.id in accepted_tripletes_ids, triplets))
            self.log(f"accepted ids: {accepted_tripletes_ids}", verbose=self.log_verbose)

        return filtered_triplets
