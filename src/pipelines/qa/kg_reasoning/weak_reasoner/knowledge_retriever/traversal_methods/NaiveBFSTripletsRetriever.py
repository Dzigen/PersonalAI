from dataclasses import dataclass, field
from typing import Dict, List, Union, Tuple
import collections
from collections import Counter
from copy import deepcopy

from ..utils import AbstractTripletsRetriever, BaseGraphSearchConfig
from .......utils.data_structs import QueryInfo, Triplet, NodeType
from .......kg_model import KnowledgeGraphModel
from .......utils.data_structs import create_id, NODES_TYPES_MAP, NodeInfo
from .......utils import Logger, accumulate_step_info, ReturnInfo
from .......utils.cache_kv import CacheUtils
from .......db_drivers.kv_driver import KeyValueDriverConfig


@dataclass
class NaiveBFSGraphSearchConfig(BaseGraphSearchConfig):
    """Конфигурация NaiveBFSTripletsRetriever-алгоритма обхода графа.

    :param max_depth: Максимальная глубина обхода графа с помощью BFS-алгоритма. Значение по умолчанию 10.
    :type max_depth: int, optional
    :param max_width: Максимальная ширина обхода графа с помощью BFS-алгоритма. Значение по умолчанию 50.
    :type max_width: int, optional
    :param max_passed_nodes: Максимальное количество вершин, которое может быть пройдено в рамках работы BFS-алгоритма. Значение по умолчанию 1000.
    :type max_passed_nodes: int, optional
    :param accepted_node_types: Типы вершин графа знаний, которые можно обходить в рамках запускаемых алгоритмов поиска/извлечения релевантной информации. Значение по умолчанию [NodeType.object, NodeType.hyper, NodeType.episodic, NodeType.time].
    :type accepted_node_types:List[Union[str, NodeType]], optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы NaiveBFSTripletsRetriever-класса. Значение по умолчанию 'qa_bfs_t_retriver_cache'.
    :type cache_table_name: str, optional
    """
    max_depth: int = 10
    max_width: int = 50
    max_passed_nodes: int = 1000
    accepted_node_types: List[Union[str, NodeType]] = field(default_factory=lambda: [NodeType.object, NodeType.hyper, NodeType.episodic, NodeType.time])
    cache_table_name: str = 'qa_bfs_t_retriver_cache'

    def to_str(self):
        str_accepted_nodes = ";".join(
            sorted(list(map(lambda v: v.value, self.accepted_node_types))))
        return f"{self.max_depth}|{self.max_width}|{self.max_passed_nodes}|{str_accepted_nodes}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = NaiveBFSGraphSearchConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self) -> None:
        for i, node_type in enumerate(self.accepted_node_types):
            if not isinstance(node_type, NodeType):
                self.accepted_node_types[i] = NODES_TYPES_MAP[node_type]


class NaiveBFSTripletsRetriever(AbstractTripletsRetriever, CacheUtils):
    """Класс предназначен для извлечения триплетов из графа знаний на основе BFS-алгоритма (обход в ширину) поиска.

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты.
    :type log: Logger
    :param search_config: Конфигурация NaiveBFSTripletsRetriever-алгоритма. Значение по умолчанию  NaiveBFSGraphSearchConfig().
    :type search_config: Union[NaiveBFSGraphSearchConfig, Dict], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: Union[None, KeyValueDriverConfig], optional
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool, optional
    """

    def __init__(self, kg_model: KnowledgeGraphModel, log: Logger, search_config: Union[NaiveBFSGraphSearchConfig, Dict] = NaiveBFSGraphSearchConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None, verbose: bool = False) -> None:
        if isinstance(search_config, dict):
            search_config = NaiveBFSGraphSearchConfig.from_dict(search_config)
        else:
            search_config.formate_fields()
        self.config: NaiveBFSGraphSearchConfig = search_config

        self.kg_model = kg_model

        self.cachekv = self.init_cachekv(cache_kvdriver_config, self.config.cache_table_name)

        self.log = log
        self.verbose = verbose

    def close_connections(self):
        if self.cachekv is not None:
            self.cachekv.close_connection()

    def clear_traversal_cache(self) -> None:
        return None

    def get_traversal_cache(self) -> None:
        return None

    def search(self, snode: NodeInfo) -> List[Triplet]:
        traversed_triplets = []
        sn_typedid = snode.to_str()
        visited, queue = set(), collections.deque([snode])
        visited.add(sn_typedid)
        D = {sn_typedid: 0}
        parent: Dict[str, Union[None, NodeInfo]] = {sn_typedid: None}
        graph_queries_counter, passed_nodes_counter = 0, 0
        max_pnodes_flag = False
        while queue:
            if max_pnodes_flag:
                break

            vertex = queue.popleft()
            vertex_typedid = vertex.to_str()

            if self.config.max_depth >= 0 and D[vertex_typedid] >= self.config.max_depth:
                # ограничиваем глубину обхода
                continue

            neighbours = self.kg_model.graph_struct.db_conn.get_adjacent_nodes(
                vertex, self.config.accepted_node_types)
            graph_queries_counter += 1

            if self.config.max_width >= 0:
                # Ограничиваем ширину обхода
                neighbours = neighbours[:self.config.max_width]

            for neighbour in neighbours:
                neighbour_typedid = neighbour.to_str()
                parent_typedid = None if parent[vertex_typedid] is None else parent[vertex_typedid].to_str()

                if neighbour_typedid == parent_typedid:
                    # пропускаем вершину, из которой пришли
                    continue

                if self.config.max_passed_nodes >= 0 and passed_nodes_counter >= self.config.max_passed_nodes:
                    # Ограничиваем количество вершин, которое можно обойти
                    max_pnodes_flag = True
                    break

                if neighbour_typedid not in visited:
                    passed_nodes_counter += 1
                    parent[neighbour_typedid] = vertex
                    D[neighbour_typedid] = D[vertex_typedid] + 1
                    visited.add(neighbour_typedid)

                    traversed_triplets += self.kg_model.graph_struct.db_conn.get_triplets(
                        vertex, neighbour)
                    graph_queries_counter += 1
                    queue.append(neighbour)

        self.log(f"bfs graph-db queries: {graph_queries_counter}", verbose=self.verbose)
        self.log(f"passed nodes counter: {passed_nodes_counter}", verbose=self.verbose)

        return traversed_triplets

    def get_cache_key(self, query_info: QueryInfo) -> List[str]:
        return [self.config.to_str(), query_info.to_str()]

    @accumulate_step_info
    @CacheUtils.cache_method_output
    def get_relevant_triplets(self, query_info: QueryInfo) -> Tuple[List[Triplet], ReturnInfo]:
        self.log("START KNOWLEDGE RETRIEVING ...", verbose=self.verbose)
        self.log("RETRIEVER: NaiveBFSTripletsRetriever", verbose=self.verbose)
        self.log(f"BASE_QUESTION ID: {create_id(query_info.query)}", verbose=self.verbose)
        self.log(f"BASE_QUESTION: {query_info.query}", verbose=self.verbose)

        rinfo = ReturnInfo()

        nodes: List[NodeInfo] = []
        unique_ntypedids = set()
        for node in query_info.linked_nodes:
            node_typedid = node.to_str()
            if node_typedid not in unique_ntypedids:
                unique_ntypedids.add(node_typedid)
                nodes.append(node)
        self.log(f"Вершины, для которых будет запущен BFS: {nodes}", verbose=self.verbose)

        unique_triplets_map: Dict[str, Triplet] = dict()
        for node in nodes:
            self.log(f"Запускаем BFS с вершины: {node}", verbose=self.verbose)
            tmp_triplets = self.search(node)
            self.log(f"Количество извлечённых триплетов для данной вершины: {len(tmp_triplets)}", verbose=self.verbose)

            for triplet in tmp_triplets:
                unique_triplets_map[triplet.relation.get_typedid()] = triplet
        unique_triplets: List[Triplet] = list(unique_triplets_map.values())

        self.log(f"Суммарное количество уникальных (по строковому представлению) извлечённых триплетов: {len(unique_triplets)}", verbose=self.verbose)
        relations_counter = Counter([triplet.relation.type for triplet in unique_triplets])
        self.log(f"Распределение типов связей в наборе извлечённых триплетов: {relations_counter}", verbose=self.verbose)

        return unique_triplets, rinfo
