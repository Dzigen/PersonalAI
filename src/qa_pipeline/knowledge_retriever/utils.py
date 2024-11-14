from typing import List
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict

from ...utils.data_structs import QueryInfo, Triplet

RETRIEVER_LOG_PATH = 'log/retriever'

class AbstractTriplesFilter(ABC):
    """Интерфейс алгоритмов фильтрации/ранжирования триплетов."""
    @abstractmethod
    def apply_filter(self, query_info: QueryInfo, triplets: List[Triplet]) -> List[Triplet]:
        """Метод предназначен для применения операциии ранжирования/фильтрации к набору триплетов на основе меры релевантности к user-вопросу.

        :param query_info: Структура данных с user-вопросом.
        :type query_info: QueryInfo
        :param triplets: Набор триплетов для ранжирования/отбора.
        :type triplets: List[Triplet]
        :return: Набор триплетов, релевантных данному user-вопрос.
        :rtype: List[Triplet]
        """
        pass

class AbstractTripletsRetriever(ABC):
    """Интерфейс алгоритмов извлечения триплетов из графа знаний."""
    @abstractmethod
    def get_relevant_triplets(self, query_info: QueryInfo) -> List[Triplet]:
        """Метод предназначен для извлечения триплетов из графа знаний на основании информации из user-вопроса. На выходе список триплетов не содержит дубликатов (по строковому представлению).

        :param query_info: Структура данных с информацией о user-вопросе.
        :type query_info: QueryInfo
        :return: Набор триплетов, извлечённый из графа знаний.
        :rtype: List[Triplet]
        """
        pass

@dataclass
class BaseGraphSearchConfig:
    """Базовая конфигурация алгоритиов по извлечению триплетов из графа знаний."""
    pass

@dataclass
class BaseTripletsFilterConfig:
    """Базовая конфигурация алгоритмоа по ранжированию/фильтрации триплетов."""
    pass
