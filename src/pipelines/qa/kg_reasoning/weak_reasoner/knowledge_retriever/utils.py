from typing import List, Dict, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass

from .errors import NOT_VALID_ID_ERROR_MSG, NO_START_NODE_IN_PARENT_ERROR_MSG, EMPTY_PARENT_ERROR_MSG
from ......utils.data_structs import QueryInfo, Triplet, NodeType, NodeInfo
from ......utils.cache_kv.CacheOperations import CacheOperations, TraversalMethodCacheOpearions
from .....utils import BaseStages

def get_nodes_path(parent: Dict[str, NodeInfo], end_node: NodeInfo) -> List[NodeInfo]:
    """Метод предназначен для получения пути обхода графа, заканчивая заданной конечной end_node_id вершиной.
    Путь должен быть ацикличным: есть стартовая вершин, у которой нет родителя.

    :param parent: Словарь с идентификаторами родительских вершин. Ключи - идентикиаторы вершин, которые были посещены; значения - идентификаторы вершины (родитель), из которой был выполнен переход в данную (ключ) вершину.
    :type parent: Dict[str, str]
    :param end_node_id: Идентификатор последней посещённой вершины.
    :type end_node_id: str
    :return: Последовательность посещённых вершин: от конечной до стартовой (в обратном порядке).
    :rtype: List[str]
    """
    if not isinstance(end_node.id, str):
        raise ValueError(NOT_VALID_ID_ERROR_MSG)
    if None not in parent.values():
        raise ValueError(NO_START_NODE_IN_PARENT_ERROR_MSG)
    if len(parent) == 0:
        raise ValueError(EMPTY_PARENT_ERROR_MSG)

    path, end_flag, cur_n = [end_node], False, end_node
    while not end_flag:
        next_n = parent[cur_n.id]
        if next_n is None:
            end_flag = True
        else:
            path.append(next_n)
            cur_n = next_n
    return path


@dataclass
class BaseTripletsFilterConfig:
    """Базовая конфигурация алгоритмов по ранжированию/фильтрации триплетов."""

    def to_str(self) -> str:
        pass


class AbstractTriplesFilter(CacheOperations):
    """Интерфейс алгоритмов фильтрации/ранжирования триплетов."""

    config: Union[None, BaseTripletsFilterConfig] = None

    @abstractmethod
    def apply_filter(self, query_info: QueryInfo, triplets: List[Triplet]) -> List[Triplet]:
        """Метод предназначен для применения операциии ранжирования/фильтрации к набору триплетов на основе меры их релевантности к user-вопросу.

        :param query_info: Структура данных с user-вопросом.
        :type query_info: QueryInfo
        :param triplets: Набор триплетов для ранжирования/отбора.
        :type triplets: List[Triplet]
        :return: Набор триплетов, релевантных данному user-вопросу.
        :rtype: List[Triplet]
        """
        pass


@dataclass
class BaseGraphSearchConfig:
    """Базовая конфигурация алгоритмов по извлечению триплетов из графа знаний."""

    def to_str(self) -> str:
        pass


class AbstractTripletsRetriever(CacheOperations, TraversalMethodCacheOpearions):
    """Интерфейс алгоритмов извлечения триплетов из графа знаний."""

    config: BaseGraphSearchConfig

    @abstractmethod
    def get_relevant_triplets(self, query_info: QueryInfo) -> List[Triplet]:
        """Метод предназначен для извлечения триплетов из графа знаний на основе информации из user-вопроса. Возвращаемый список триплетов не содержит дубликатов (по строковому представлению).

        :param query_info: Структура данных с информацией о user-вопросе.
        :type query_info: QueryInfo
        :return: Набор триплетов, извлечённый из графа знаний.
        :rtype: List[Triplet]
        """
        pass


@dataclass
class KnowledgeRetrieverStages:
    triplets_retriever: AbstractTripletsRetriever
    triplets_filter: Union[None, AbstractTriplesFilter] = None
