from typing import List
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict

from ...utils.data_structs import QueryInfo, Triplet

RETRIEVER_LOG_PATH = 'log/retriever'

class AbstractTriplesFilter(ABC):
    @abstractmethod
    def apply_filter(self, query_info: QueryInfo, triplets: List[Triplet]) -> List[Triplet]:
        """_summary_

        :param query_info: _description_
        :type query_info: QueryInfo
        :param triplets: _description_
        :type triplets: List[Triplet]
        :return: _description_
        :rtype: List[Triplet]
        """
        # фильтрация триплетов по заданному правилу
        pass

class AbstractTripletsRetriever(ABC):
    @abstractmethod
    def get_relevant_triplets(self, query_info: QueryInfo) -> List[Triplet]:
        """_summary_

        :param query_info: _description_
        :type query_info: QueryInfo
        :return: _description_
        :rtype: List[Triplet]
        """
        # извлечение триплетов из графа знаний, релевантных запросу
        pass

@dataclass
class BaseGraphSearchConfig:
    pass

@dataclass
class BaseTripletsFilterConfig:
    pass
