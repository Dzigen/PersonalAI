from dataclasses import dataclass
from typing import List

from .utils import AbstractTriplesFilter
from ...utils.data_structs import Triplet, QueryInfo
from ...utils import Logger
from ...knowledge_graph_model import KnowledgeGraphModel
from ...db_drivers.vector_driver import VectorDBInstance

@dataclass
class TripletsFilterConfig:
    max_k: int = 50

class TripletsFilter(AbstractTriplesFilter):
    """Главный класс для фильтрации триплетов, извлечённых из графа знаний,
    на основе их релевантности пользовательскому запросу.
    """

    def __init__(self, kg_model: KnowledgeGraphModel, log: Logger, config: TripletsFilterConfig, log_verbose: bool = False) -> None:
        """_summary_

        :param kg_model: _description_
        :type kg_model: KnowledgeGraphModel
        :param log: _description_
        :type log: Logger
        :param config: _description_
        :type config: TripletsFilterConfig
        :param log_verbose: _description_, defaults to False
        :type log_verbose: bool, optional
        """
        self.log = log
        self.log_verbose = log_verbose
        self.kg_model = kg_model
        self.config = config

    def apply_filter(self, query_info: QueryInfo, triplets: List[Triplet]) -> List[Triplet]:
        """_summary_

        :param query_info: _description_
        :type query_info: QueryInfo
        :param triplets: _description_
        :type triplets: List[Triplet]
        :return: _description_
        :rtype: List[Triplet]
        """
        filtered_triplets = []
        query_embd = self.kg_model.embeddings_struct.embedder.encode_queries([query_info.query])[0]
        query_instance = VectorDBInstance(embedding=query_embd)
        base_triplets_ids = list(map(lambda triplet: triplet.id, triplets))
        try:
            if len(base_triplets_ids) > 0:
                raw_relevant_triplets = self.kg_model.embeddings_struct.vectordbs['triplets'].retrieve(
                    [query_instance], self.config.max_k, includes=['embeddings', 'documents', 'metadatas'], where={"id": {"$in": base_triplets_ids}})[0]
                accepted_tripletes_ids = list(map(lambda item: item[1].id, raw_relevant_triplets))
                filtered_triplets = list(filter(lambda triplet: triplet.id in accepted_tripletes_ids, triplets))

                self.log(f"accepted ids: {accepted_tripletes_ids}", verbose=self.log_verbose)
        except Exception as e:
            print(f"error in apply_filter: {e}")
            filtered_triplets = triplets[:self.config.max_k]
        if len(filtered_triplets) < self.config.max_k:
            filtered_triplets = triplets[:self.config.max_k]
        return filtered_triplets
