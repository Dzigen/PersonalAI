from typing import List
from dataclasses import dataclass
from collections import Counter

from .utils import AbstractTripletsRetriever, BaseGraphSearchConfig
from ......db_drivers.vector_driver import VectorDBInstance
from ......kg_model import KnowledgeGraphModel
from ......utils import Logger
from ......utils.data_structs import QueryInfo, Triplet, create_id

@dataclass
class NaiveGraphSearchConfig(BaseGraphSearchConfig):
    max_k: int = 50

class NaiveTripletsRetriever(AbstractTripletsRetriever):

    def __init__(self, kg_model: KnowledgeGraphModel, log: Logger, search_config: NaiveGraphSearchConfig = NaiveGraphSearchConfig(),
                 verbose: bool = False) -> None:
        self.log = log
        self.verbose = verbose
        self.kg_model = kg_model
        self.config = search_config

    def get_relevant_triplets(self, query_info: QueryInfo) -> List[Triplet]:
        self.log("START KNOWLEDGE RETRIEVING ...", verbose=self.verbose)
        self.log(f"BASE_QUESTION ID: {create_id(query_info.query)}", verbose=self.verbose)
        self.log(f"BASE_QUESTION: {query_info.query}", verbose=self.verbose)

        query_embd = self.kg_model.embeddings_struct.embedder.encode_queries([query_info.query])[0]
        query_instance = VectorDBInstance(embedding=query_embd)

        raw_relevant_triplets = self.kg_model.embeddings_struct.vectordbs['triplets'].retrieve(
                [query_instance], self.config.max_k, includes=['metadatas'])[0]

        triplet_ids = list(map(lambda item: item[1].metadata['t_id'], raw_relevant_triplets))
        self.log(f"Количество извлечённых объектов из векторной бд (triplets): {len(triplet_ids)}", verbose=self.verbose)

        triplets = self.kg_model.graph_struct.db_conn.read(triplet_ids)
        self.log(f"Количество полученных трипелтов из графовой бд: {len(triplets)}", verbose=self.verbose)
        self.log(f"Распределение типов связей в наборе извлечённых триплетов: {Counter([triplet.relation.type for triplet in triplets])}", verbose=self.verbose)

        return triplets
