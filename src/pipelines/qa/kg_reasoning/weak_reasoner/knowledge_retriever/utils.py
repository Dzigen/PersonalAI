from typing import List, Dict, Union, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass

from .errors import NOT_VALID_ID_ERROR_MSG, NO_START_NODE_IN_PARENT_ERROR_MSG, EMPTY_PARENT_ERROR_MSG
from ......utils.data_structs import QueryInfo, Triplet, NodeInfo, BaseConfigOperations, NodeType
from ......utils.cache_kv.CacheOperations import CacheOperations, TraversalMethodCacheOpearions


def get_nodes_path(parent: Dict[str, NodeInfo], end_node: NodeInfo) -> List[NodeInfo]:
    """Метод предназначен для получения пути обхода графа, заканчивая заданной конечной end_node_id вершиной.
    Путь должен быть ацикличным: есть стартовая вершина, у которой нет родителя.

    :param parent: Словарь с идентификаторами родительских вершин. Ключи - идентификаторы вершин, которые были посещены; значения - идентификаторы вершины (родитель), из которой был выполнен переход в данную (ключ) вершину.
    :type parent: Dict[str, NodeInfo]
    :param end_node_id: Идентификатор последней посещённой вершины.
    :type end_node_id: str
    :return: Последовательность посещённых вершин: от конечной до стартовой (в обратном порядке).
    :rtype: List[NodeInfo]
    """
    if not isinstance(end_node.id, str):
        raise ValueError(NOT_VALID_ID_ERROR_MSG)
    if None not in parent.values():
        raise ValueError(NO_START_NODE_IN_PARENT_ERROR_MSG)
    if len(parent) == 0:
        raise ValueError(EMPTY_PARENT_ERROR_MSG)

    path, end_flag, cur_n = [end_node], False, end_node
    while not end_flag:
        next_n = parent[cur_n.to_str()]
        if next_n is None:
            end_flag = True
        else:
            path.append(next_n)
            cur_n = next_n
    return path


@dataclass
class BaseTripletsFilterConfig(BaseConfigOperations):
    """Базовая конфигурация алгоритмов по ранжированию/фильтрации триплетов."""


class AbstractTriplesFilter(CacheOperations):
    """Интерфейс алгоритмов фильтрации/ранжирования триплетов."""

    config: Union[None, BaseTripletsFilterConfig] = None

    @abstractmethod
    def apply_filter(self, query_info: QueryInfo, triplets: List[Triplet]) -> List[Triplet]:
        """Метод предназначен для применения операции ранжирования/фильтрации к набору триплетов на основе меры их релевантности к user-вопросу.

        :param query_info: Структура данных с user-вопросом.
        :type query_info: QueryInfo
        :param triplets: Набор триплетов для ранжирования/отбора.
        :type triplets: List[Triplet]
        :return: Набор триплетов, релевантных данному user-вопросу.
        :rtype: List[Triplet]
        """
        pass

    @abstractmethod
    def close_connections(self):
        pass


@dataclass
class BaseGraphSearchConfig(BaseConfigOperations):
    """Базовая конфигурация алгоритмов по извлечению триплетов из графа знаний."""
    accepted_node_types: Union[List[NodeType], None] = None


class AbstractTripletsRetriever(TraversalMethodCacheOpearions):
    """Интерфейс алгоритмов извлечения триплетов из графа знаний."""

    config: BaseGraphSearchConfig

    @abstractmethod
    def get_relevant_triplets(self, query_info: QueryInfo) -> Tuple[List[Triplet], bool]:
        """Метод предназначен для извлечения триплетов из графа знаний на основе информации из user-вопроса. Возвращаемый список триплетов не содержит дубликатов (по строковому представлению).

        :param query_info: Структура данных с информацией о user-вопросе.
        :type query_info: QueryInfo
        :return: Кортеж из двух объектов: (1) Набор триплетов, извлечённый из графа знаний; (2) True, если результат был получен из кеша (cache hit), иначе False.
        :rtype: Tuple[List[Triplet], bool]
        """
        pass

    @abstractmethod
    def close_connections(self):
        pass


@dataclass
class KnowledgeRetrieverStages:
    """Контейнер стадий knowledge retriever пайплайна.

    :param triplets_retriever: Реализация алгоритма извлечения триплетов.
    :type triplets_retriever: QueryInfo
    :param triplets_filter: Реализация алгоритма фильтрации/ранжирования триплетов. Значение по умолчанию None.
    :type triplets_filter: Union[None, AbstractTriplesFilter], optional
    """
    triplets_retriever: AbstractTripletsRetriever
    triplets_filter: Union[None, AbstractTriplesFilter] = None

    def close_connections(self):
        self.triplets_retriever.close_connections()
        if self.triplets_filter is not None:
            self.triplets_filter.close_connections()
