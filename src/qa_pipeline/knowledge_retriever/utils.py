from typing import List
from abc import ABC, abstractmethod
from typing import Dict

from ...utils.data_structs import QueryInfo, Triplet

LOG_PATH = 'retriever_log'

class AbstractTriplesFilter(ABC):
    @abstractmethod
    def apply_filter(self, query_info: QueryInfo, triplets: List[Triplet]) -> List[Triplet]:
        # фильтрация триплетов по заданному правилу
        pass

class AbstractTripletsRetriever(ABC):
    @abstractmethod
    def get_relevant_triplets(self, query_info: QueryInfo) -> List[Triplet]:
        # извлечение триплетов из графа знаний, релевантных запросу
        pass


class AbstractGraphDriver(ABC):
    @abstractmethod
    def get_adjecent_nodes(self, base_node_id: str, parent_node_id: str) -> List[str]:
        # получение списка смежных с данной вершин, без вершины из которой пришли ранее
        pass