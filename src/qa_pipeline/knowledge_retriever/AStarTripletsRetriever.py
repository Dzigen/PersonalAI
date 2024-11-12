from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import numpy as np
import heapq
from time import time
import collections
from copy import deepcopy

from .utils import AbstractTripletsRetriever, BaseGraphSearchConfig
from ...utils.data_structs import QueryInfo, Triplet, NodeType
from ...knowledge_graph_model import KnowledgeGraphModel
from ...utils.data_structs import create_id_for_node_pair
from ...db_drivers.kv_driver.utils import AbstractKVDatabaseConnection, KeyValueDBInstance
from ...db_drivers.kv_driver import KeyValueDriverConfig, KeyValueDriver
from ...utils import Logger

@dataclass
class AStarMetricsConfig:
    #
    h_metric_name: str = 'ip' # 'ip', 'weight_with_short_path', 'avg_weighted_with_short_path'
    kvdriver_config: KeyValueDriverConfig = None

@dataclass
class AStarGraphSearchConfig(BaseGraphSearchConfig):
    #
    metrics_config: AStarMetricsConfig = field(default_factory=lambda: AStarMetricsConfig())
    # макимальная глубина обхода графа для поиска заданной вершины
    max_depth: int = 10 # int number or -1
    # максимальное количество вершин графа, которые можно обойти для поиска заднной вершины
    max_passed_nodes: int = 500 # int number or -1
    # типы вершин, которые можно обходить во время поиска заданной вершины
    accepted_node_types: List[NodeType] = field(default_factory=lambda:[NodeType.object , NodeType.hyper, NodeType.episodic])

class AStarMetrics:
    """Класс предназначен для расчёта d- и h-метрик, испрльзуемых в рамках A*алгоритма поиска."""
    def __init__(self, kg_model: KnowledgeGraphModel, accepted_node_types: str, log: Logger,
                config: AStarMetricsConfig = AStarMetricsConfig(), verbose: bool = False):
        self.config = config
        self.accepted_node_types = accepted_node_types
        self.kg_model = kg_model
        self.log = log
        self.verbose = verbose

        # костыль
        if self.config.kvdriver_config is not None:
            self.cache = dict()
            if self.config.h_metric_name in ['ip', 'weight_with_short_path',  'avg_weighted_with_short_path']:
                ip_config = deepcopy(config.kvdriver_config)
                ip_config.db_config.db_info['table'] = 'ip'
                self.cache['ip'] = KeyValueDriver.connect(ip_config)
            if self.config.h_metric_name in ['weight_with_short_path',  'avg_weighted_with_short_path']:
                sp_config = deepcopy(config.kvdriver_config)
                sp_config.db_config.db_info['table'] = 'bfs_short_path'
                self.cache['bfs_short_path'] = KeyValueDriver.connect(sp_config)

        self.cache_info = {
            'dist': {'exist': 0, 'calc': 0},
            'bfs_short_path': {'exist': 0, 'calc': 0}
        }

        self.metrics_map = {
            'ip': self.precomputed_dist,
            'weight_with_short_path': self.weighted_short_path,
            'avg_weighted_with_short_path': self.avg_weighted_short_path,
        }

    def compute_h_metric(self, *args, **kwargs) -> float:
        """_summary_

        :return: _description_
        :rtype: float
        """
        return self.metrics_map[self.config.h_metric_name](*args, **kwargs)

    def get_nodes_path(self, parent: Dict[str, str], end_node_id: str) -> List[str]:
        """_summary_

        :param parent: _description_
        :type parent: Dict[str, str]
        :param end_node_id: _description_
        :type end_node_id: str
        :return: _description_
        :rtype: List[str]
        """
        #end_node_id = U[-1] if (end_node_id not in parent) else end_node_id
        path, end_flag, cur_n = [end_node_id], False, end_node_id
        while not end_flag:
            next_n = parent[cur_n]
            if next_n is None:
                end_flag = True
            else:
                path.append(next_n)
                cur_n = next_n
        return path

    def precomputed_dist(self, node1_id: str, node2_id: str, *args, **kwargs) -> float:
        """_summary_

        :param node1_id: _description_
        :type node1_id: str
        :param node2_id: _description_
        :type node2_id: str
        :return: _description_
        :rtype: float
        """
        def _calculate_node_distance(id1: str, id2: str) -> float:
            dist = 0
            if node1_id != node2_id:
                instances = self.kg_model.embeddings_struct.vectordbs['nodes'].read([node1_id, node2_id], includes=['embeddings'])
                # calculation ip distance
                dist = 1 - np.dot(instances[0].embedding, instances[1].embedding)
            return dist

        if self.config.kvdriver_config is not None:
            pair_id = create_id_for_node_pair(node1_id, node2_id)
            if self.cache['ip'].item_exist(pair_id):
                #print("exists")
                dist = self.cache['ip'].read([pair_id])[0]['v']
                self.cache_info['dist']['exist'] += 1
            else:
                #print("calculating")
                dist = _calculate_node_distance(node1_id, node2_id)
                self.cache['ip'].create([KeyValueDBInstance(id=pair_id, metadata={'v': dist})])
                self.cache_info['dist']['calc'] += 1
        else:
            dist = _calculate_node_distance(node1_id, node2_id)

        return dist

    def bfs(self, s_node_id, e_node_id):
        """_summary_

        :param s_node_id: _description_
        :type s_node_id: _type_
        :param e_node_id: _description_
        :type e_node_id: _type_
        :return: _description_
        :rtype: _type_
        """
        visited, queue = set(), collections.deque([s_node_id])
        visited.add(s_node_id)
        D = {s_node_id: 0}
        parent = {s_node_id: None}
        neo4j_queries_counter, passed_nodes_counter = 0, 0
        while queue:
            #print(len(queue))
            vertex = queue.popleft()
            neighbours = self.kg_model.graph_struct.db_conn.get_adjecent_nodes(vertex, self.accepted_node_types)
            neo4j_queries_counter += 1
            for neighbour in neighbours:

                if neighbour == parent[vertex]:
                    # пропускаем вершину, из которой пришли
                    continue

                if neighbour not in visited:
                    parent[neighbour] = vertex
                    D[neighbour] = D[vertex] + 1
                    visited.add(neighbour)
                    passed_nodes_counter += 1

                    if self.config.kvdriver_config is not None:
                        pair_id = create_id_for_node_pair(s_node_id, neighbour)
                        if not self.cache['bfs_short_path'].item_exist(pair_id):
                            self.cache['bfs_short_path'].create([KeyValueDBInstance(id=pair_id, metadata={'v': D[neighbour]})])

                    if neighbour == e_node_id:
                        self.log(f"bfs end-node found!", verbose=self.verbose)
                        self.log(f"bfs graph-db queries: {neo4j_queries_counter}", verbose=self.verbose)
                        self.log(f"passed nodes: {passed_nodes_counter}", verbose=self.verbose)
                        return D[neighbour]

                    queue.append(neighbour)

        # между вершинами нет пути
        self.log(f"bfs not found end-node", verbose=self.verbose)
        self.log(f"bfs graph-db queries: {neo4j_queries_counter}", verbose=self.verbose)
        self.log(f"passed nodes: {passed_nodes_counter}", verbose=self.verbose)

        INF_VALUE = 1000001 # специальное значение, которое говорит, что между вершинами нет пути
        if self.config.kvdriver_config is not None:
            pair_id = create_id_for_node_pair(s_node_id, e_node_id)
            if not self.cache['bfs_short_path'].item_exist(pair_id):
                self.cache['bfs_short_path'].create([KeyValueDBInstance(id=pair_id, metadata={'v': INF_VALUE})])

        return INF_VALUE

    def precomputed_short_path(self, node1_id: str, node2_id: str) -> float:
        """_summary_

        :param node1_id: _description_
        :type node1_id: str
        :param node2_id: _description_
        :type node2_id: str
        :return: _description_
        :rtype: float
        """
        pair_id = create_id_for_node_pair(node1_id, node2_id)
        if self.cache['bfs_short_path'].item_exist(pair_id):
            #print("exists")
            short_path = self.cache['bfs_short_path'].read([pair_id])[0]['v']
            self.cache_info['bfs_short_path']['exist'] += 1
        else:
            #print("calculating")
            short_path = self.bfs(node1_id, node2_id)
            self.cache['bfs_short_path'].create([KeyValueDBInstance(id=pair_id, metadata={'v': short_path})])
            self.cache_info['bfs_short_path']['calc'] += 1

        return short_path

    def weighted_short_path(self, node1_id: str, node2_id: str, *args, **kwargs) -> float:
        """_summary_

        :param node1_id: _description_
        :type node1_id: str
        :param node2_id: _description_
        :type node2_id: str
        :return: _description_
        :rtype: float
        """
        short_path_len = self.precomputed_short_path(node1_id, node2_id)
        w = self.precomputed_dist(node1_id, node2_id)
        return short_path_len * w

    def avg_weighted_short_path(self, node1_id: str, node2_id: str, parent: Dict[str, str]) -> float:
        """_summary_

        :param node1_id: _description_
        :type node1_id: str
        :param node2_id: _description_
        :type node2_id: str
        :param parent: _description_
        :type parent: Dict[str, str]
        :return: _description_
        :rtype: float
        """
        nodes_path = self.get_nodes_path(parent, node1_id)
        acc_dist = 0
        for i in range(len(nodes_path)-1):
            acc_dist += self.precomputed_dist(nodes_path[i], nodes_path[i+1])
        acc_dist += self.precomputed_dist(node1_id, node2_id)

        short_path_len = self.precomputed_short_path(node1_id, node2_id)
        return np.mean(acc_dist) * short_path_len

class AStarGraphSearch:
    """Класс предназначен для запуска A*-алгоритма поиска."""

    def __init__(self, kg_model: KnowledgeGraphModel, log: Logger, search_config: AStarGraphSearchConfig = AStarGraphSearchConfig(),
                 verbose: bool = False) -> None:
        self.log = log
        self.verbose = verbose
        self.config = search_config
        self.kg_model = kg_model
        self.metrics = AStarMetrics(
            kg_model=kg_model, accepted_node_types=self.config.accepted_node_types,
            log=self.log, config=self.config.metrics_config, verbose=verbose)

    def search_path(self, start_node_id: str, end_node_id: str) -> Tuple[List[str], List[str], Dict[str, int], Dict[str, str], str]:
        """_summary_

        :param start_node_id: _description_
        :type start_node_id: str
        :param end_node_id: _description_
        :type end_node_id: str
        :return: _description_
        :rtype: Tuple[List[str], List[str], Dict[str, int], Dict[str, str], str]
        """
        # использованная реализация A*-алгоритма поиска кратчайшего пути между вершинами: https://www.redblobgames.com/pathfinding/a-star/implementation.html
        frontier = []
        heapq.heappush(frontier, (0, start_node_id))
        parent = {start_node_id: None}
        cost_so_far = {start_node_id: 0}
        D = {start_node_id: 0}

        spare_closest_node_id = start_node_id
        passed_nodes_counter = 0
        while len(frontier):
            current_node_id = heapq.heappop(frontier)[1]
            passed_nodes_counter += 1

            if (self.config.max_passed_nodes >= 0) and (passed_nodes_counter >= self.config.max_passed_nodes):
                self.log("PASSED LIMIT OF MAX NODES", verbose=self.verbose)
                break

            if (self.config.max_depth >= 0) and (D[current_node_id] >= self.config.max_depth):
                self.log("PASSED MAX DEPTH LIMIT", verbose=self.verbose)
                continue

            # Сохраняем промежуточную вершину, до которой есть путь.
            # Если не будет найден путь до end_node, то будет использован путь до spare_closest_node
            spare_closest_node_id = current_node_id

            #
            if current_node_id == end_node_id:
                self.log("FOUND END-NODE", verbose=self.verbose)
                break

            adj_nodes = self.kg_model.graph_struct.db_conn.get_adjecent_nodes(current_node_id, self.config.accepted_node_types)
            self.log(f"adjenced nodes: {len(adj_nodes)}", verbose=self.verbose)

            for adj_n_id in adj_nodes:

                if adj_n_id == parent[current_node_id]:
                    # пропускаем вершину, из которой пришли
                    continue

                new_cost = cost_so_far[current_node_id] + 1 # работаем с невзвешенным графом
                if (adj_n_id not in cost_so_far) or (new_cost < cost_so_far[adj_n_id]):
                    parent[adj_n_id] = current_node_id
                    D[adj_n_id] = D[current_node_id] + 1

                    cost_so_far[adj_n_id] = new_cost
                    priority = new_cost + self.metrics.compute_h_metric(adj_n_id, end_node_id, parent)
                    heapq.heappush(frontier, (priority, adj_n_id))

        self.log(f"start-spare node path len: {D[spare_closest_node_id]}" if end_node_id not in parent else f"start-end node path len: {D[end_node_id]}", verbose=self.verbose)
        self.log(f"astar neo4j queries: {passed_nodes_counter}", verbose=self.verbose)
        return cost_so_far, frontier, D, parent, spare_closest_node_id

class AStarTripletsRetriever(AbstractTripletsRetriever):
    """Класс предназначен для извлечения триплетов из графа знаний на основе A*-алгоритма поиска.1"""

    def __init__(self, kg_model: KnowledgeGraphModel, log: Logger, search_config: AStarGraphSearchConfig = AStarGraphSearchConfig(),
                 verbose: bool = False) -> None:
        self.log = log
        self.verbose = verbose
        self.kg_model = kg_model
        self.graph_searcher = AStarGraphSearch(kg_model, log, search_config, verbose)

    def get_nodes_path(self, parent: Dict[str, str], end_node_id: str, spare_closest_node_id: str) -> List[str]:
        """_summary_

        :param parent: _description_
        :type parent: Dict[str, str]
        :param end_node_id: _description_
        :type end_node_id: str
        :param spare_closest_node_id: _description_
        :type spare_closest_node_id: str
        :return: _description_
        :rtype: List[str]
        """
        end_node_id = spare_closest_node_id if (end_node_id not in parent) else end_node_id

        path, end_flag, cur_n = [end_node_id], False, end_node_id
        while not end_flag:
            next_n = parent[cur_n]
            if next_n is None:
                end_flag = True
            else:
                path.append(next_n)
                cur_n = next_n

        return path

    def get_relevant_triplets(self, query_info: QueryInfo) -> List[Triplet]:
        nodes_ids = []
        for node in query_info.linked_nodes:
            if node.id not in nodes_ids:
                nodes_ids.append(node.id)
        unique_nodes_pairs = set()

        all_pair_nodes_counter = sum(list(range(len(nodes_ids))))
        pair_nodes_counter = 0
        if len(nodes_ids) > 1:
            self.log("pair nodes calculation...", verbose=self.verbose)
            for i in range(len(nodes_ids)-1):
                start_node = nodes_ids[i]
                for j in range(i+1, len(nodes_ids)):
                    pair_nodes_counter += 1
                    self.log(f"{all_pair_nodes_counter} / {pair_nodes_counter}", verbose=self.verbose)
                    end_node = nodes_ids[j]

                    s_time = time()
                    _, _, _, parent, spare_closest_node = self.graph_searcher.search_path(start_node, end_node)
                    self.log(f"search elapsed_time: {time() - s_time}", verbose=self.verbose)

                    s_time = time()
                    nodes_path = self.get_nodes_path(parent, end_node, spare_closest_node)
                    self.log(f"get_path elapsed_time: {time() - s_time}", verbose=self.verbose)

                    # Сохраняем только уникальные пары вершин (по их идентификаторам)
                    s_time = time()
                    unique_nodes_pairs.update([(nodes_path[i], nodes_path[i+1]) for i in range(len(nodes_path)-1)] if len(nodes_path) > 1 else [])
                    self.log(f"saving_nodes elapsed_time: {time() - s_time}", verbose=self.verbose)

                    self.log(self.graph_searcher.metrics.cache_info, verbose=self.verbose)

        # Сохраняем только уникальные триплеты (по их строковым представлениям)
        self.log("pair nodes formating...", verbose=self.verbose)
        s_time = time()
        unique_triplets = dict()
        for nodes_pair in unique_nodes_pairs:
            triplets = self.kg_model.graph_struct.db_conn.get_triplets(*nodes_pair)
            for triplet in triplets:
                unique_triplets[triplet.id] = triplet

        self.log(f"foramting neo4j queries: {len(unique_nodes_pairs)}", verbose=self.verbose)
        self.log(f"= formating elapsed_time: {time() - s_time}", verbose=self.verbose)

        return list(unique_triplets.values())
