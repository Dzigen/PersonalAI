from dataclasses import dataclass, field
from typing import Dict, List, Union
import collections
from collections import Counter

from ..utils import AbstractTripletsRetriever, BaseGraphSearchConfig
from .......utils.data_structs import QueryInfo, Triplet, NodeType
from .......kg_model import KnowledgeGraphModel
from .......utils.data_structs import create_id, NODES_TYPES_MAP
from .......utils import Logger
from .......utils.cache_kv import CacheUtils
from .......db_drivers.kv_driver import KeyValueDriverConfig


@dataclass
class NaiveBFSGraphSearchConfig(BaseGraphSearchConfig):
    """Конфигурация NaiveBFSTripletsRetriever-алгоритма обхода графа.

    :param max_depth: Максимальная глубина обхода графа с помощью BFS-алгоритма. Значение по умолчанию 10.
    :type max_depth: int, optional
    :param max_width: Максимальная ширина обхода графа с помощью BFS-алгоритма. Значение по умолчанию 50.
    :type max_width: int, optional
    :param max_passed_nodes: Максимальное количество вершин, которое может пройдено в рамках работы BFS-алгоритма. Значение по умолчанию 1000.
    :type max_passed_nodes: int, optional
    :param accepted_node_types: Типы вершин графа знаний, которые можно обходить в рамках запускаемых алгоритмов поиска/извелчения релевантной информации. Значение по умолчанию [NodeType.object, NodeType.hyper, NodeType.episodic, NodeType.time].
    :type accepted_node_types: List[NodeType], optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы NaiveBFSTripletsRetriever-класса. Значение по умолчанию 'qa_bfs_t_retriver_cache'.
    :type cache_table_name: str, optional
    """
    max_depth: int = 10
    max_width: int = 50
    max_passed_nodes: int = 1000
    accepted_node_types: List[NodeType] = field(default_factory=lambda: [
                                                NodeType.object, NodeType.hyper, NodeType.episodic, NodeType.time])
    cache_table_name: str = 'qa_bfs_t_retriver_cache'

    def to_str(self):
        str_accepted_nodes = ";".join(
            sorted(list(map(lambda v: v.value, self.accepted_node_types))))
        return f"{self.max_depth}|{self.max_width}|{self.max_passed_nodes}|{str_accepted_nodes}"


class NaiveBFSTripletsRetriever(AbstractTripletsRetriever, CacheUtils):
    """Класс предназначен для извлечения триплетов из графа знаний на основе BFS-алгоритма (обход в ширину) поиска.

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты.
    :type log: Logger
    :param search_config: Конфигурация NaiveBFSTripletsRetriever-алгоритма. Значение по умолчанию  NaiveBFSGraphSearchConfig().
    :type search_config: Union[NaiveBFSGraphSearchConfig, Dict], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: Union[None,KeyValueDriverConfig], optional
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool, optional
    """

    def __init__(self, kg_model: KnowledgeGraphModel, log: Logger, search_config: Union[NaiveBFSGraphSearchConfig, Dict] = NaiveBFSGraphSearchConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None, verbose: bool = False) -> None:
        if type(search_config) is dict:
            if 'accepted_node_types' in search_config:
                search_config['accepted_node_types'] = list(
                    map(lambda k: NODES_TYPES_MAP[k], search_config['accepted_node_types']))
            search_config = NaiveBFSGraphSearchConfig(**search_config)
        self.config = search_config

        self.kg_model = kg_model

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, self.config.cache_table_name)

        self.log = log
        self.verbose = verbose

    def clear_kv_caches(self, level='all') -> None:
        if type(level) is not str:
            raise TypeError(
                f"Аргумент переменной 'level' должен иметь тип 'str'; сейчас аргумент имеет тип '{type(level)}'")
        if level not in ['all', 'current', 'other']:
            raise ValueError(
                f"Аргумент переменной 'level' должен принимать одно из трёх значенией: 'all', 'current' или 'other'. Полученное значение: '{level}'")

        if level in ['current', 'all']:
            self.cachekv.clear()

        if level == 'other':
            raise NotImplementedError

    def search(self, node_id: str) -> List[Triplet]:
        traversed_triplets = []
        visited, queue = set(), collections.deque([node_id])
        visited.add(node_id)
        D = {node_id: 0}
        parent = {node_id: None}
        neo4j_queries_counter, passed_nodes_counter = 0, 0
        max_pnodes_flag = False
        while queue:
            if max_pnodes_flag:
                break

            vertex = queue.popleft()

            if self.config.max_depth >= 0 and D[vertex] >= self.config.max_depth:
                # ограничиваем глубину обхода
                continue

            neighbours = self.kg_model.graph_struct.db_conn.get_adjecent_nids(
                vertex, self.config.accepted_node_types)
            neo4j_queries_counter += 1

            if self.config.max_width >= 0:
                # Ограничиваем ширину обхода
                neighbours = neighbours[:self.config.max_width]

            for neighbour in neighbours:

                if neighbour == parent[vertex]:
                    # пропускаем вершину, из которой пришли
                    continue

                if self.config.max_passed_nodes >= 0 and passed_nodes_counter >= self.config.max_passed_nodes:
                    # Ограничиваем количество вершин, которое можно обойти
                    max_pnodes_flag = True
                    break

                if neighbour not in visited:
                    passed_nodes_counter += 1
                    parent[neighbour] = vertex
                    D[neighbour] = D[vertex] + 1
                    visited.add(neighbour)

                    traversed_triplets += self.kg_model.graph_struct.db_conn.get_triplets(
                        vertex, neighbour)
                    neo4j_queries_counter += 1
                    queue.append(neighbour)

        self.log(
            f"bfs graph-db queries: {neo4j_queries_counter}", verbose=self.verbose)
        self.log(
            f"passed nodes counter: {passed_nodes_counter}", verbose=self.verbose)

        return traversed_triplets

    def get_cache_key(self, query_info: QueryInfo) -> List[str]:
        return [self.config.to_str(), query_info.to_str()]

    @CacheUtils.cache_method_output
    def get_relevant_triplets(self, query_info: QueryInfo) -> List[Triplet]:
        self.log("START KNOWLEDGE RETRIEVING ...", verbose=self.verbose)
        self.log("RETRIEVER: NaiveBFSTripletsRetriever", verbose=self.verbose)
        self.log(
            f"BASE_QUESTION ID: {create_id(query_info.query)}", verbose=self.verbose)
        self.log(f"BASE_QUESTION: {query_info.query}", verbose=self.verbose)

        node_ids = set([node.id for node in query_info.linked_nodes])
        self.log(
            f"Вершины, для которых будет запущейн BFS: {node_ids}", verbose=self.verbose)

        unique_triplets = dict()
        for node_id in node_ids:
            self.log(
                f"Запускаем BFS по вершине с id: {node_id}", verbose=self.verbose)
            tmp_triplets = self.search(node_id)
            self.log(
                f"Количество извлечённых триплетов для данной вершины: {len(tmp_triplets)}", verbose=self.verbose)
            unique_triplets.update(
                {triplet.relation.id: triplet for triplet in tmp_triplets})

        self.log(
            f"Суммарное количество уникальных (по строковому представлению) извлечённых триплетов: {len(unique_triplets)}", verbose=self.verbose)
        self.log(
            f"Распределение типов связей в наборе извлечённых триплетов: {Counter([triplet.relation.type for triplet in unique_triplets.values()])}", verbose=self.verbose)

        return list(unique_triplets.values())
