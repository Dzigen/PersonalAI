from typing import List
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict

from ...utils.data_structs import QueryInfo, Triplet

RETRIEVER_LOG_PATH = 'log/retriever'

class AbstractTriplesFilter(ABC):
    "Интерфейс для алгоритмов фильтрации/ранжирования триплетов.
    @abstractmethod
    def apply_filter(self, query_info: QueryInfo, triplets: List[Triplet]) -> List[Triplet]:
        """Метод предназначен для применения операциии ранжирования/фильтрации к набору триплетов на основе метрики релевантности к user-вопросу.

        :param query_info: Структура данных с user-вопросом.
        :type query_info: QueryInfo
        :param triplets: Набор триплетов для ранжирования/отбора.
        :type triplets: List[Triplet]
        :return: Набор триплетов, релевантных данному user-вопрос.
        :rtype: List[Triplet]
        """
        # фильтрация триплетов по заданному правилу
        pass

class AbstractTripletsRetriever(ABC):
    """Базовый класс для алгоритмов извлечения триплетов из графа знаний"""
    @abstractmethod
    def get_relevant_triplets(self, query_info: QueryInfo) -> List[Triplet]:
        """Метод предназначен для извлечения триплетов из графа знаний на основании инфлрмации из user-вопроса. На выхрде список триплетов не содержит дубликатов (по строковому представлению).

        :param query_info: Структура данных с информацией о user-вопросе
        :type query_info: QueryInfo
        :return: Набор триплетов, извлечённый из графа знаний.
        :rtype: List[Triplet]
        """
        # извлечение триплетов из графа знаний, релевантных запросу
        pass

@dataclass
class BaseGraphSearchConfig:
    "Базовая конфигурация для алгоритиов по извлечению триплетов из графа знаний."
    pass

@dataclass
class BaseTripletsFilterConfig:
    "Базовая конфигурация для алгоритмоа по ранжированию/фильтрации триплетов
    pass
