from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Union
import numpy as np
import heapq
from time import time
import collections
from copy import deepcopy
from collections import Counter

from ..utils import AbstractTripletsRetriever, BaseGraphSearchConfig, get_nodes_path, NodeInfo
from .......utils.data_structs import QueryInfo, Triplet, NodeType, create_id_for_node_pair, create_id, \
    NODES_TYPES_MAP, NodeInfo, from_str_to_nodeinfo, BaseConfigOperations
from .......kg_model import KnowledgeGraphModel
from .......db_drivers.kv_driver import KeyValueDriverConfig, KeyValueDriver, KeyValueDBInstance
from .......utils import Logger
from .......utils.cache_kv import CacheUtils
from .......db_drivers.kv_driver.utils import AbstractKVDatabaseConnection
from .......db_drivers.vector_driver import VectorDBInstance


@dataclass
class AStarMetricsConfig(BaseConfigOperations):
    """Конфигурация класса для расчёта метрик, используемых в рамках A*-алгоритма.

    :param h_metric_name: Эвристическая метрика, которая будет использоваться для оценки расстояния между текущей и конечной вершинами. Данное поле может принимать следующие значения: (1) 'ip' - косинусное расстояние между эмбеддингами текущей и конечной вершин; (2) 'weight_with_short_path' - кратчайшее расстояние между текущей и конечной вершинами (полученное с помощью bfs-алгоритма), домноженное на 'ip'-метрику; (3) 'avg_weighted_with_short_path' - кратчайшее расстояние между текущей и конечной вершинами (полученное с помощью bfs-алгоритма), домноженное на усреднённое значение 'ip'-метрики между парами вершин в пути от начальной до текущей вершины + пара из текущей и конечной вершин. Значение по умолчанию 'ip'.
    :type h_metric_name: str, optional
    :param nodes_vdb_name: ... . Значение по умолчанию 'nodes_dense'.
    :type nodes_vdb_name: str, optional
    :param kvdriver_config: Конфигурация кеша для хранения рассчитанных h-оценок между вершинами. Значение по умолчанию None (кеширование не используется). Значение по умолчанию None.
    :type kvdriver_config: Union[None, KeyValueDriverConfig, Dict], optional
    """
    h_metric_name: str = 'ip'
    nodes_vdb_name: str = 'nodes_dense'
    kvdriver_config: Union[None, KeyValueDriverConfig, Dict] = None

    def to_str(self):
        return f"{self.h_metric_name}"

    @staticmethod
    def from_dict(dict_config: Dict):
        formated_config = AStarMetricsConfig(**dict_config)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.kvdriver_config, dict):
            self.kvdriver_config = KeyValueDriverConfig.from_dict(self.kvdriver_config)
        elif self.kvdriver_config is not None:
            self.kvdriver_config.formate_fields()


class AStarMetrics:
    """Класс предназначен для расчёта d- и h-метрик, используемых в рамках A*-алгоритма поиска.

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param config: Конфигурация класса. Значение по умолчанию AStarMetricsConfig().
    :type config: AStarMetricsConfig
    :param accepted_node_types: Типы вершин, которые можно использовать при расчёте метрик.
    :type accepted_node_types: List[NodeType]
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты. Значение по умолчанию Logger(RETRIEVER_LOG_PATH).
    :type log: Logger
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool
    """
    cache: Union[None, Dict[str, AbstractKVDatabaseConnection]] = None

    def __init__(self, kg_model: KnowledgeGraphModel, accepted_node_types: List[NodeType], log: Logger,
                 config: AStarMetricsConfig = AStarMetricsConfig(), verbose: bool = False):
        self.config = config
        self.accepted_node_types = accepted_node_types
        self.kg_model = kg_model

        # проверка: в указанной бд должны содержатся плотные (dense) векторные предаставления вершин, иначе вызываем исключение
        for _, v_composer in self.kg_model.graph_embeddings.nodes_vcomposers.items():
            if not hasattr(v_composer.vdb_conn_mapping[self.config.nodes_vdb_name], 'embedder'):
                raise ValueError

        self.init_kv_caches()

        self.metrics_map = {
            'ip': self.embeddings_dist,
            'weight_with_short_path': self.weighted_short_path,
            'avg_weighted_with_short_path': self.avg_weighted_short_path,
        }

        self.log = log
        self.verbose = verbose

    def init_caches_stats(self) -> None:
        self.cache_info = {
            'dist': {'exist': 0, 'calc': 0},
            'bfs_short_path': {'exist': 0, 'calc': 0},
            'weight_with_short_path': {'exist': 0, 'calc': 0},
            'avg_weighted_with_short_path': {'exist': 0, 'calc': 0}
        }

    def init_kv_caches(self) -> None:
        if self.config.kvdriver_config is not None:
            self.cache: Dict[str, AbstractKVDatabaseConnection] = dict()
            if self.config.h_metric_name in ['ip', 'weight_with_short_path', 'avg_weighted_with_short_path']:
                ip_config = deepcopy(self.config.kvdriver_config)
                ip_config.db_config.db_info['table'] = 'astar_retriever_ip'
                self.cache['ip'] = KeyValueDriver.connect(ip_config)
            if self.config.h_metric_name in ['weight_with_short_path', 'avg_weighted_with_short_path']:
                sp_config = deepcopy(self.config.kvdriver_config)
                sp_config.db_config.db_info['table'] = 'astar_retriever_bfsshortpath'
                self.cache['bfs_short_path'] = KeyValueDriver.connect(
                    sp_config)

                sp_config = deepcopy(self.config.kvdriver_config)
                sp_config.db_config.db_info['table'] = 'astar_retriever_weightwithshortpath'
                self.cache['weight_with_short_path'] = KeyValueDriver.connect(
                    sp_config)

                sp_config = deepcopy(self.config.kvdriver_config)
                sp_config.db_config.db_info['table'] = 'astar_retriever_avgweightedwithshortpath'
                self.cache['avg_weighted_with_short_path'] = KeyValueDriver.connect(
                    sp_config)

        self.init_caches_stats()

    def clear_kv_caches(self) -> None:
        for key in self.cache.keys():
            self.cache[key].clear()
        self.init_caches_stats()

    def compute_h_metric(self, *args, **kwargs) -> float:
        return self.metrics_map[self.config.h_metric_name](*args, **kwargs)

    def calculate_ip_distance(self, node1: NodeInfo, node2: NodeInfo) -> float:
        dist = 0
        if node1.id != node2.id:
            instances: List[VectorDBInstance] = []
            for node in [node1, node2]:
                instances.append(self.kg_model.graph_embeddings.nodes_vcomposers[node.type].read(
                    [node.id], vdb_name=self.config.nodes_vdb_name, includes=['embeddings'])[0])
            # calculation ip distance
            try:
                dist = 1 - np.dot(instances[0].embedding, instances[1].embedding)
            except IndexError:
                print(f"Error instances:\n- {instances[0]}\n- {instances[1]}")
                raise IndexError

        return dist

    def embeddings_dist(self, node1: NodeInfo, node2: NodeInfo, *args, **kwargs) -> float:
        if self.config.kvdriver_config is not None:
            pair_id = create_id_for_node_pair(node1.to_str(), node2.to_str())
            if self.cache['ip'].item_exist(pair_id):
                # print("exists")
                dist = self.cache['ip'].read([pair_id])[0].value
                self.cache_info['dist']['exist'] += 1
            else:
                # print("calculating")
                dist = self.calculate_ip_distance(node1, node2)
                self.cache['ip'].create(
                    [KeyValueDBInstance(id=pair_id, value=dist)])
                self.cache_info['dist']['calc'] += 1
        else:
            dist = self.calculate_ip_distance(node1, node2)
            self.cache_info['dist']['calc'] += 1

        return dist

    def compute_short_path(self, node1: NodeInfo, node2: NodeInfo) -> float:
        if self.config.kvdriver_config is not None:
            pair_id = create_id_for_node_pair(node1.to_str(), node2.to_str())
            if self.cache['bfs_short_path'].item_exist(pair_id):
                # print("exists")
                short_path = self.cache['bfs_short_path'].read([pair_id])[0].value
                self.cache_info['bfs_short_path']['exist'] += 1
            else:
                # print("calculating")
                short_path = self.bfs(node1, node2)
                self.cache['bfs_short_path'].create([KeyValueDBInstance(id=pair_id, value=short_path)])
                self.cache_info['bfs_short_path']['calc'] += 1
        else:
            short_path = self.bfs(node1, node2)
            self.cache_info['bfs_short_path']['calc'] += 1

        return short_path

    def weighted_short_path(self, node1: NodeInfo, node2: NodeInfo, *args, **kwargs) -> float:
        pair_id = create_id_for_node_pair(node1.to_str(), node2.to_str())
        if (self.config.kvdriver_config is not None) and (self.cache['weight_with_short_path'].item_exist(pair_id)):
            # print("exists")
            w_short_path = self.cache['weight_with_short_path'].read([pair_id])[0].value
            self.cache_info['weight_with_short_path']['exist'] += 1
        else:
            # print("calculated")
            short_path_len = self.compute_short_path(node1, node2)
            w = self.embeddings_dist(node1, node2)
            w_short_path = w * short_path_len
            self.cache['weight_with_short_path'].create([KeyValueDBInstance(id=pair_id, value=w_short_path)])
            self.cache_info['weight_with_short_path']['calc'] += 1

        return w_short_path

    def avg_weighted_short_path(self, node1: NodeInfo, node2: NodeInfo, parent: Dict[str, Union[None, NodeInfo]]) -> float:
        pair_id = create_id_for_node_pair(node1.to_str(), node2.to_str())
        if (self.config.kvdriver_config is not None) and (self.cache['avg_weighted_with_short_path'].item_exist(pair_id)):
            # print("exists")
            avg_w_short_path = self.cache['avg_weighted_with_short_path'].read([pair_id])[0].value
            self.cache_info['avg_weighted_with_short_path']['exist'] += 1
        else:
            # print("calculated")
            nodes_path = get_nodes_path(parent, node1)
            acc_dist = 0
            for i in range(len(nodes_path) - 1):
                acc_dist += self.embeddings_dist(nodes_path[i], nodes_path[i + 1])
            acc_dist += self.embeddings_dist(node1, node2)

            short_path_len = self.compute_short_path(node1, node2)
            avg_w_short_path = np.mean(acc_dist) * short_path_len

            self.cache['avg_weighted_with_short_path'].create(
                [KeyValueDBInstance(id=pair_id, value=avg_w_short_path)])
            self.cache_info['avg_weighted_with_short_path']['calc'] += 1

        return avg_w_short_path

    def bfs(self, s_node: NodeInfo, e_node: NodeInfo) -> int:
        sn_typedid, en_typedid = s_node.to_str(), e_node.to_str()
        visited, queue = set(), collections.deque([s_node])
        visited.add(sn_typedid)
        D: Dict[str, int] = {sn_typedid: 0}
        parent: Dict[str, NodeInfo] = {sn_typedid: None}
        graph_queries_counter, passed_nodes_counter = 0, 0

        while queue:
            # print(len(queue))
            vertex = queue.popleft()
            vertex_typedid = vertex.to_str()

            neighbours = self.kg_model.graph_struct.db_conn.get_adjecent_nodes(
                vertex, self.accepted_node_types)
            graph_queries_counter += 1
            for neighbour in neighbours:
                neighbour_typedid = neighbour.to_str()
                parent_typedid = None if parent[vertex_typedid] is None else parent[vertex_typedid].to_str()
                if neighbour_typedid == parent_typedid:
                    # пропускаем вершину, из которой пришли
                    continue

                if neighbour_typedid not in visited:
                    passed_nodes_counter += 1
                    parent[neighbour_typedid] = vertex
                    D[neighbour_typedid] = D[vertex_typedid] + 1
                    visited.add(neighbour_typedid)

                    if self.config.kvdriver_config is not None:
                        # кешируем кратчайший bfs-путь от s_node_id-стартовой до текущей вершины
                        pair_id = create_id_for_node_pair(sn_typedid, neighbour_typedid)
                        if not self.cache['bfs_short_path'].item_exist(pair_id):
                            self.cache['bfs_short_path'].create(
                                [KeyValueDBInstance(id=pair_id, value=D[neighbour_typedid])])
                            self.cache_info['bfs_short_path']['calc'] += 1

                        # кешируем кратчайший bfs-путь от vertex-вершины до его соседа (путь равен 1)
                        pair_id = create_id_for_node_pair(vertex_typedid, neighbour_typedid)
                        if not self.cache['bfs_short_path'].item_exist(pair_id):
                            self.cache['bfs_short_path'].create(
                                [KeyValueDBInstance(id=pair_id, value=1)])
                            self.cache_info['bfs_short_path']['calc'] += 1

                    if neighbour_typedid == en_typedid:
                        self.log(f"bfs end-node found!", verbose=self.verbose)
                        self.log(f"bfs graph-db queries: {graph_queries_counter}", verbose=self.verbose)
                        self.log(f"passed nodes: {passed_nodes_counter}", verbose=self.verbose)

                        # костыль
                        self.cache_info['bfs_short_path']['calc'] -= 1

                        # кешируем кратчайшие bfs-пути от e_node_id-вершины до вершин,
                        # которые были в кратчайшем пути между s_node_id- и e_node_id-вершинами
                        reverse_nodes_path = get_nodes_path(parent, neighbour)
                        for i in range(1, len(reverse_nodes_path) - 1):
                            pair_id = create_id_for_node_pair(
                                reverse_nodes_path[i].to_str(), neighbour_typedid)
                            if not self.cache['bfs_short_path'].item_exist(pair_id):
                                self.cache['bfs_short_path'].create(
                                    [KeyValueDBInstance(id=pair_id, value=i)])
                                self.cache_info['bfs_short_path']['calc'] += 1

                        return D[neighbour_typedid]

                    queue.append(neighbour)

        # между вершинами нет пути
        self.log(f"bfs not found end-node", verbose=self.verbose)
        self.log(f"bfs graph-db queries: {graph_queries_counter}", verbose=self.verbose)
        self.log(f"passed nodes: {passed_nodes_counter}", verbose=self.verbose)

        INF_VALUE = 1000001  # специальное значение, которое говорит, что между вершинами нет пути
        if self.config.kvdriver_config is not None:
            pair_id = create_id_for_node_pair(sn_typedid, en_typedid)
            if not self.cache['bfs_short_path'].item_exist(pair_id):
                self.cache['bfs_short_path'].create([KeyValueDBInstance(id=pair_id, value=INF_VALUE)])

        return INF_VALUE


@dataclass
class AStarGraphSearchConfig(BaseGraphSearchConfig):
    """Конфигурация класса, реализующего логику A*-алгоритма поиска по графу знаний.

    :param metrics_config: Конфигурация класса, выполняющая расчёт необходимых метрик для A*-алгоритма. Значение по умолчанию AStarMetricsConfig().
    :type metrics_config: Union[Dict,AStarMetricsConfig]
    :param max_depth: Максимальная глубина обхода графа для поиска заданной вершины. Если указано значение -1, то данное ограничение выключается. Значение по умолчанию 10.
    :type max_depth: int
    :param max_passed_nodes: Максимальное количество вершин, которое можно обойти для поиска заданной вершины в графе. Если указано значение -1, то данное ограничение выключается. Значение по умолчанию 500.
    :type max_passed_nodes: int
    :param accepted_node_types: Типы вершин, которые можно обходить во время поиска заданной вершины. Значение по умолчанию [NodeType.object, NodeType.hyper, NodeType.episodic].
    :type accepted_node_types: List[Union[str,NodeType]]
    """
    metrics_config: Union[Dict, AStarMetricsConfig] = field(default_factory=lambda: AStarMetricsConfig())
    max_depth: int = 10
    max_passed_nodes: int = 500
    accepted_node_types: List[Union[str, NodeType]] = field(default_factory=lambda: [
        NodeType.object, NodeType.hyper, NodeType.episodic, NodeType.time])
    cache_table_name: str = 'qa_astar_t_retriever_cache'

    def to_str(self):
        str_accepted_nodes = ";".join(
            sorted(list(map(lambda v: v.value, self.accepted_node_types))))
        return f"{self.metrics_config.to_str()}|{self.max_depth}|{self.max_passed_nodes}|{str_accepted_nodes}"

    @staticmethod
    def from_dict(dict_config: Dict):
        formated_config = AStarGraphSearchConfig(**dict_config)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self) -> None:
        for i, node_type in enumerate(self.accepted_node_types):
            if not isinstance(node_type, NodeType):
                self.accepted_node_types[i] = NODES_TYPES_MAP[node_type]

        if self.metrics_config is dict:
            self.metrics_config = AStarMetricsConfig.from_dict(self.metrics_config)
        else:
            self.metrics_config.formate_fields()


class AStarGraphSearch:
    """Класс предназначен для запуска A*-алгоритма с целью извлечения триплетов из графового хранилища триплетов.

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param search_config: Конфигурация A*-алгоритма поиска по графовому хранилищу триплетов. Значение по умолчанию AStarGraphSearchConfig().
    :type search_config: AStarGraphSearchConfig
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты. Значение по умолчанию Logger(RETRIEVER_LOG_PATH).
    :type log: Logger
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool
    """

    def __init__(self, kg_model: KnowledgeGraphModel, log: Logger, search_config: AStarGraphSearchConfig = AStarGraphSearchConfig(),
                 verbose: bool = False) -> None:
        self.config = search_config
        self.kg_model = kg_model
        self.metrics = AStarMetrics(kg_model=kg_model, accepted_node_types=self.config.accepted_node_types,
                                    log=log, config=self.config.metrics_config, verbose=verbose)

        self.log = log
        self.verbose = verbose

    def search_path(self, start_node: NodeInfo, end_node: NodeInfo) -> Tuple[List[str], List[NodeInfo], Dict[str, int], Dict[str, NodeInfo], NodeInfo]:
        """Реализация A*-алгоритма. Источник: https://www.redblobgames.com/pathfinding/a-star/implementation.html."""
        frontier: List[int, NodeInfo] = []
        heapq.heappush(frontier, (0, start_node))
        parent: Dict[str, Union[None, NodeInfo]] = {start_node.to_str(): None}
        cost_so_far: Dict[str, int] = {start_node.to_str(): 0}
        D: Dict[str, int] = {start_node.to_str(): 0}

        end_node_typedid = end_node.to_str()
        spare_closest_node = start_node
        passed_nodes_counter = 0
        while len(frontier):
            current_node: NodeInfo = heapq.heappop(frontier)[1]
            current_node_typedid = current_node.to_str()
            passed_nodes_counter += 1

            if (self.config.max_passed_nodes >= 0) and (passed_nodes_counter >= self.config.max_passed_nodes):
                self.log("PASSED LIMIT OF MAX NODES", verbose=self.verbose)
                break

            if (self.config.max_depth >= 0) and (D[current_node_typedid] >= self.config.max_depth):
                self.log("PASSED MAX DEPTH LIMIT", verbose=self.verbose)
                continue

            # Сохраняем промежуточную вершину, до которой есть путь.
            # Если не будет найден путь до end_node, то будет использован путь до spare_closest_node
            spare_closest_node = current_node

            #
            if current_node_typedid == end_node_typedid:
                self.log("FOUND END-NODE", verbose=self.verbose)
                break

            adj_nodes = self.kg_model.graph_struct.db_conn.get_adjecent_nodes(
                current_node, self.config.accepted_node_types)
            # self.log(f"adjenced nodes: {len(adj_nodes)}", verbose=self.verbose)

            for adj_node in adj_nodes:

                parent_node_typedid = None if parent[current_node_typedid] is None else parent[current_node_typedid].to_str()
                adj_node_typedid = adj_node.to_str()
                if adj_node_typedid == parent_node_typedid:
                    # пропускаем вершину, из которой пришли
                    continue

                # работаем с невзвешенным графом
                new_cost = cost_so_far[current_node_typedid] + 1
                if (adj_node_typedid not in cost_so_far) or (new_cost < cost_so_far[adj_node_typedid]):
                    parent[adj_node_typedid] = current_node
                    D[adj_node_typedid] = D[current_node_typedid] + 1

                    cost_so_far[adj_node_typedid] = new_cost
                    priority = new_cost + self.metrics.compute_h_metric(adj_node, end_node, parent)
                    heapq.heappush(frontier, (priority, adj_node))

        if end_node_typedid not in parent:
            self.log(f"start-spare node path len: {D[spare_closest_node.to_str()]}", verbose=self.verbose)
        else:
            self.log(f"start-end node path len: {D[end_node_typedid]}", verbose=self.verbose)
        self.log(f"astar queries: {passed_nodes_counter}", verbose=self.verbose)
        return cost_so_far, frontier, D, parent, spare_closest_node


class AStarTripletsRetriever(AbstractTripletsRetriever, CacheUtils):
    """Класс предназначен для извлечения триплетов из графа знаний на основе A*-алгоритма поиска.

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param search_config: Конфигурация A*-алгоритма поиска по графовому хранилищу триплетов. Значение по умолчанию AStarGraphSearchConfig().
    :type search_config: Union[AStarGraphSearchConfig, Dict], optional
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты.
    :type log: Logger
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: Union[None,KeyValueDriverConfig], optional
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool, optional
    """

    def __init__(self, kg_model: KnowledgeGraphModel, log: Logger, search_config: Union[AStarGraphSearchConfig, Dict] = AStarGraphSearchConfig(),
                 cache_kvdriver_config: KeyValueDriverConfig = None, verbose: bool = False) -> None:
        if isinstance(search_config, dict):
            search_config = AStarGraphSearchConfig.from_dict(search_config)
        else:
            search_config.formate_fields()
        self.config: AStarGraphSearchConfig = search_config

        self.kg_model = kg_model

        self.graph_searcher = AStarGraphSearch(kg_model, log, search_config, verbose)

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, self.config.cache_table_name)

        self.log = log
        self.verbose = verbose

    def clear_traversal_cache(self) -> None:
        self.graph_searcher.metrics.clear_kv_caches()

    def get_traversal_cache(self) -> Dict[str, Union[None, Dict[str, int]]]:
        cache_info = None
        if self.graph_searcher.metrics.cache is not None:
            cache_info = {cache_name: cache_obj.count_items() for cache_name, cache_obj in self.graph_searcher.metrics.cache.items()}

        return {
            'AStarMetrics': cache_info
        }

    def get_cache_key(self, query_info: QueryInfo) -> List[str]:
        return [self.config.to_str(), query_info.to_str()]

    @CacheUtils.cache_method_output
    def get_relevant_triplets(self, query_info: QueryInfo) -> List[Triplet]:
        self.log("START KNOWLEDGE RETRIEVING ...", verbose=self.verbose)
        self.log("RETRIEVER: AStarTripletsRetriever", verbose=self.verbose)
        self.log(f"BASE_QUESTION ID: {create_id(query_info.query)}", verbose=self.verbose)
        self.log(f"BASE_QUESTION: {query_info.query}", verbose=self.verbose)

        #
        nodes: List[NodeInfo] = []
        unique_ntypedids = set()
        for node in query_info.linked_nodes:
            node_typedid = node.to_str()
            if node_typedid not in unique_ntypedids:
                unique_ntypedids.add(node_typedid)
                nodes.append(node)
        self.log(f"unique nodes: {nodes}", verbose=self.verbose)

        #
        unique_nodes_pairs = set()
        all_pair_nodes_counter = sum(list(range(len(nodes))))
        pair_nodes_counter = 0
        if len(nodes) > 1:
            self.log("pair nodes calculation...", verbose=self.verbose)
            for i in range(len(nodes) - 1):
                start_node = nodes[i]
                for j in range(i + 1, len(nodes)):
                    pair_nodes_counter += 1
                    self.log(f"{all_pair_nodes_counter} / {pair_nodes_counter}", verbose=self.verbose)
                    end_node = nodes[j]

                    s_time = time()
                    _, _, _, parent, spare_closest_node = self.graph_searcher.search_path(start_node, end_node)
                    self.log(f"search elapsed_time: {time() - s_time}", verbose=self.verbose)

                    s_time = time()
                    nodes_path = get_nodes_path(parent, spare_closest_node if end_node.to_str() not in parent else end_node)
                    self.log(f"get_path elapsed_time: {time() - s_time}", verbose=self.verbose)

                    # Сохраняем только уникальные пары вершин (по их идентификаторам)
                    s_time = time()
                    unique_nodes_pairs.update([(nodes_path[i].to_str(), nodes_path[i + 1].to_str()) for i in range(len(nodes_path) - 1)] if len(nodes_path) > 1 else [])
                    self.log(f"saving_nodes elapsed_time: {time() - s_time}", verbose=self.verbose)

                    self.log(self.graph_searcher.metrics.cache_info, verbose=self.verbose)

        # Сохраняем только уникальные триплеты (по их строковым представлениям)
        self.log("pair nodes formating...", verbose=self.verbose)
        s_time = time()
        unique_triplets_map: Dict[str, Triplet] = dict()
        for raw_nodes_pair in unique_nodes_pairs:
            node1, node2 = from_str_to_nodeinfo(raw_nodes_pair[0]), from_str_to_nodeinfo(raw_nodes_pair[1])
            triplets = self.kg_model.graph_struct.db_conn.get_triplets(node1, node2)
            for triplet in triplets:
                unique_triplets_map[triplet.relation.get_typedid()] = triplet
        unique_triplets: List[Triplet] = list(unique_triplets_map.values())

        self.log(f"Распределение типов связей в наборе извлечённых триплетов: {Counter([triplet.relation.type for triplet in unique_triplets])}", verbose=self.verbose)
        self.log(f"foramting queries: {len(unique_nodes_pairs)}", verbose=self.verbose)
        self.log(f"formating elapsed_time: {time() - s_time}", verbose=self.verbose)

        return unique_triplets
