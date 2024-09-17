from typing import List
from abc import ABC, abstractmethod

from ...utils.data_structs import QueryInfo, Triplet

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
