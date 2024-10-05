from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import joblib
import numpy as np
from time import time

from .utils import AbstractTripletsRetriever, AbstractGraphDriver
from .cache import KeyValueStore
from ...utils.data_structs import QueryInfo, Node, Relation, Triplet, NodeCreator, TripletCreator, NodeType
from ...knowledge_graph_model import KnowledgeGraphModel
from ...neo4j_functions import AbstractGraphConnection
from ...utils.data_structs import NODES_TYPES_MAP, RELATIONS_TYPES_MAP, create_id_for_node_pair
from ...embedding_functions import ChromaConnection
from ...utils import Logger

@dataclass
class AStarMetricsConfig:
    d_metric_name: str = 'ip'
    h_metric_name: str = 'ip' #'weight_with_short_path'

@dataclass
class AStarGraphSearchConfig:
    metrics_config: AStarMetricsConfig = field(default_factory=lambda: AStarMetricsConfig())
    max_depth: int = 10
    accepted_node_types: str = f'["{NodeType.object.value}","{NodeType.hyper.value}","{NodeType.episodic.value}"]'

class Neo4jGraphDriver(AbstractGraphDriver):
    
    def get_adjecent_nodes(self, base_node_id: str, parent_node_id: str, accepted_n_types: str) -> List[str]:
        raw_nodes = self.kg_model.graph_db.execute_query(
            f'MATCH (a)-[r]-(b) WHERE elementId(a) = "{base_node_id}" AND elementId(b) <> "{parent_node_id}" AND ANY(lbl in {accepted_n_types} where lbl in labels(b)) RETURN b')
        formated_nodes = [node['b'].element_id for node in raw_nodes]
        return formated_nodes
    
    def get_raw_triplet(self, node1_id: str, node2_id: str):
        output = self.kg_model.graph_db.execute_query(
            f'MATCH (n1)-[rel]-(n2) WHERE elementId(n1) = "{node1_id}" AND elementId(n2) = "{node2_id}" RETURN n1, rel, n2')
        if not len(output):
            raise ValueError
        return output[0] 

def getAStarGraphSearcher(graph_driver: AbstractGraphDriver = Neo4jGraphDriver):

    class AStarMetrics(Neo4jGraphDriver):
        def __init__(self, kg_model: KnowledgeGraphModel, accepted_node_types: str, log: Logger, 
                     config: AStarMetricsConfig = AStarMetricsConfig(), cache: KeyValueStore = None,
                     log_verbose: bool = False):
            super().__init__()

            self.log = log
            self.log_verbose = log_verbose
            self.kg_model = kg_model
            self.cache = cache
            self.config = config
            self.accepted_node_types = accepted_node_types

            self.cache_info = {
                'dist': {'exist': 0, 'calc': 0},
                'short_path': {'exist': 0, 'calc': 0}
            }

            self.metrics_map = {
                'ip': self.precomputed_dist,
                'constant': lambda v1, v2, U, parent: 1,
                'weight_with_short_path': self.weighted_short_path,
                'avg_weighted_with_short_path': self.avg_weighted_short_path,
            }

        def compute_d_metric(self, *args, **kwargs) -> float:
            return self.metrics_map[self.config.d_metric_name](*args, **kwargs)

        def compute_h_metric(self, *args, **kwargs) -> float:
            return self.metrics_map[self.config.h_metric_name](*args, **kwargs)

        def get_nodes_path(self, parent: Dict[str, str], U: List[str], end_node_id: str) -> List[str]:
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
            pair_id = create_id_for_node_pair(node1_id, node2_id)
            cache_key = ('test', 'dist', pair_id)
            dist = None
            if self.cache.is_key_exists(cache_key):
                #print("exists")
                dist = self.cache.get_value_by_key(cache_key)['v']
                self.cache_info['dist']['exist'] += 1
            else:
                #print("calculating")
                if node1_id != node2_id:
                    instances = self.kg_model.embeddings_db.vectordbs['nodes'].read([node1_id, node2_id], includes=['embeddings'])
                    # calculation ip distance 
                    dist = 1 - np.dot(instances[0].embedding, instances[1].embedding)
                else:
                    dist = 0
                self.cache.save_kv_pair(cache_key, {'v': dist})
                self.cache_info['dist']['calc'] += 1
                
            return dist

        def dijkstra(self, s_node_id, e_node_id):
            # Используемая реализация алгоритма Дейкстры: https://ru.wikibooks.org/wiki/%D0%A0%D0%B5%D0%B0%D0%BB%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D0%B8_%D0%B0%D0%BB%D0%B3%D0%BE%D1%80%D0%B8%D1%82%D0%BC%D0%BE%D0%B2/%D0%90%D0%BB%D0%B3%D0%BE%D1%80%D0%B8%D1%82%D0%BC_%D0%94%D0%B5%D0%B9%D0%BA%D1%81%D1%82%D1%80%D1%8B
            available_nodes = {s_node_id: 0}
            parent = {s_node_id: None}
            passed_nodes_counter = 0
            while len(available_nodes) > 0:
                min_weight = 1000001
                ID_min_weight = -1
                for node_id, weight in available_nodes.items():
                    if weight < min_weight:
                        min_weight = weight
                        ID_min_weight = node_id
                
                if ID_min_weight == e_node_id:
                    self.log(f"passed nodes: {passed_nodes_counter}", verbose=self.log_verbose)
                    if self.cache is not None:
                        pair_id = create_id_for_node_pair(s_node_id, ID_min_weight)
                        cache_key = ('test', 'short_path', pair_id)
                        if not self.cache.is_key_exists(cache_key):
                            self.cache.save_kv_pair(cache_key, {'v': available_nodes[ID_min_weight]})
                    return min_weight

                adjenced_nodes_ids = self.get_adjecent_nodes(ID_min_weight, parent[ID_min_weight], self.accepted_node_types)

                for adj_n_id in adjenced_nodes_ids:
                    if (adj_n_id not in available_nodes) or ((available_nodes[ID_min_weight] + 1) < available_nodes[adj_n_id]):
                        available_nodes[adj_n_id] = available_nodes[ID_min_weight] + 1
                        parent[adj_n_id] = ID_min_weight
                
                pair_id = create_id_for_node_pair(s_node_id, ID_min_weight)
                cache_key = ('test', 'short_path', pair_id)
                if not self.cache.is_key_exists(cache_key):
                    self.cache.save_kv_pair(cache_key, {'v': available_nodes[ID_min_weight]})
                del available_nodes[ID_min_weight]
                passed_nodes_counter += 1

            # между вершинами нет пути
            self.log(f"passed nodes: {passed_nodes_counter}", verbose=self.log_verbose)
            return 1000001

        def precomputed_short_path(self, node1_id: str, node2_id: str) -> float:
            pair_id = create_id_for_node_pair(node1_id, node2_id)
            cache_key = ('test', 'short_path', pair_id)
            if self.cache.is_key_exists(cache_key):
                #print("exists")
                short_path = self.cache.get_value_by_key(cache_key)['v']
                self.cache_info['short_path']['exist'] += 1
            else:
                #print("calculating")
                short_path = self.dijkstra(node1_id, node2_id)
                self.cache_info['short_path']['calc'] += 1

            return short_path

        def weighted_short_path(self, node1_id: str, node2_id: str, *args, **kwargs) -> float:
            short_path_len = self.precomputed_short_path(node1_id, node2_id)
            w = self.precomputed_dist(node1_id, node2_id)
            return short_path_len * w

        def avg_weighted_short_path(self, node1_id: str, node2_id: str, U: List[str], parent: Dict[str, str]) -> float:
            nodes_path = self.get_nodes_path(parent, U, node1_id)
            acc_dist = 0
            for i in range(len(nodes_path)-1):
                acc_dist += self.precomputed_dist(nodes_path[i], nodes_path[i+1])
            acc_dist += self.precomputed_dist(node1_id, node2_id)

            short_path_len = self.precomputed_short_path(node1_id, node2_id)
            return np.mean(acc_dist) * short_path_len

    class AStarGraphSearch(graph_driver):
        """Класс с реализацией A*-алгоритма поиска по графу"""

        def __init__(self, kg_model: KnowledgeGraphModel, log: Logger, search_config: AStarGraphSearchConfig = AStarGraphSearchConfig(),
                     cache: KeyValueStore = None, log_verbose: bool = False) -> None:
            super().__init__()

            self.log = log
            self.log_verbose = log_verbose
            self.config = search_config
            self.kg_model = kg_model
            self.metrics = AStarMetrics(
                kg_model, self.config.accepted_node_types, self.log, config=self.config.metrics_config, 
                cache=cache, log_verbose=log_verbose)

        def get_min_f_node(self, Q: List[str], f: Dict[str, float]) -> Dict:
            min_idx = 0
            min_node_id = Q[min_idx]
            min_f = f[min_node_id]
            
            for idx in range(1, len(Q)):
                if f[Q[idx]] < min_f:
                    min_idx = idx
                    min_node_id = Q[min_idx]
                    min_f = f[min_node_id]
                    
            return min_node_id, min_idx 

        def search_path(self, start_node_id: str, end_node_id: str) -> Tuple[List[str], List[str], Dict[str, int], Dict[str, str], str]:
            U, Q, D = [], [start_node_id], {start_node_id: 0}
            g = {start_node_id: 0}
            parent = {start_node_id: None}
            f = {start_node_id: g[start_node_id] + self.metrics.compute_h_metric(start_node_id, end_node_id, U, parent)}
            
            spare_closest_node_id = start_node_id
            passed_nodes_counter = 0
            while len(Q) != 0:

                current_node_id, current_node_idx = self.get_min_f_node(Q, f) # вершина из Q с минимальным значением f
                passed_nodes_counter += 1

                # Сохраняем промежуточную вершину, до которой есть путь. 
                # Если не будет найден путь до end_node, то будет использован путь до spare_closest_node
                if self.metrics.compute_h_metric(
                    current_node_id, end_node_id, U, parent) <= self.metrics.compute_h_metric(
                        spare_closest_node_id, end_node_id, U, parent):
                    if f[current_node_id] <= f[spare_closest_node_id]:
                        spare_closest_node_id = current_node_id
                
                #
                if current_node_id == end_node_id:
                    break

                del Q[current_node_idx]
                if D[current_node_id] >= self.config.max_depth:
                    continue
                U.append(current_node_id)

                adj_nodes = self.get_adjecent_nodes(current_node_id, parent[current_node_id], self.config.accepted_node_types)
                #print("adjenced nodes: ", len(adj_nodes))

                for adj_n_id in adj_nodes:
                    tentativeScore = g[current_node_id] + self.metrics.compute_d_metric(current_node_id, adj_n_id, U, parent)      
                    if (adj_n_id in U) and (tentativeScore >= g[adj_n_id]):
                        continue
                    if (adj_n_id not in U) or (tentativeScore < g[adj_n_id]):
                        parent[adj_n_id] = current_node_id
                        g[adj_n_id] = tentativeScore
                        f[adj_n_id] = g[adj_n_id] + self.metrics.compute_d_metric(adj_n_id, end_node_id, U, parent)
                        D[adj_n_id] = D[current_node_id] + 1

                        if adj_n_id not in Q:
                            Q.append(adj_n_id)

            self.log(f"neo4j queries: {passed_nodes_counter}", verbose=self.log_verbose)
            return U, Q, D, parent, spare_closest_node_id
        
    return AStarGraphSearch
    
class AStartTripletsRetriever(AbstractTripletsRetriever):
    """Главный класс для извлечения триплетов из графа знаний, релевантных запросу, на основе A*-алгоритма поиска.

    Args:
        AStarGraphSearch: A* алгоритм поиска по графу знаний.
        AbstractTripletsRetriever: Интерфейс для классов с алгоритма извлечения релевантных триплетов из графов знаний.
    """
    
    def __init__(self, kg_model: KnowledgeGraphModel, log: Logger, search_config: AStarGraphSearchConfig = AStarGraphSearchConfig(), 
                 cache: KeyValueStore = None, log_verbose: bool = False) -> None:
        self.log = log
        self.log_verbose = log_verbose
        self.graph_searcher = getAStarGraphSearcher()(kg_model, log, search_config, cache, log_verbose)

    def get_formated_triplet(self, nodes_pair: Tuple[str, str]) -> Dict[str,Triplet]:
        raw_triplet = self.graph_searcher.get_raw_triplet(nodes_pair[0], nodes_pair[1])
        #print(nodes_pair, raw_triplet)
        
        node1 = NodeCreator.create(id=raw_triplet['n1'].element_id, name=str(raw_triplet['n1']['name']), 
                                        type=NODES_TYPES_MAP[list(raw_triplet['n1'].labels)[0]],
                                        prop=dict(raw_triplet['n1']))
        node2 = NodeCreator.create(id=raw_triplet['n2'].element_id, name=str(raw_triplet['n2']['name']), 
                                        type=NODES_TYPES_MAP[list(raw_triplet['n2'].labels)[0]],
                                        prop=dict(raw_triplet['n2']))
        relation = Relation(id=raw_triplet['rel'].element_id, name=str(raw_triplet['rel']['name']), 
                            type=RELATIONS_TYPES_MAP[raw_triplet['rel'].type], 
                            prop=dict(raw_triplet['rel']))
        
        start_node_id = raw_triplet['rel'].nodes[0].element_id
        start_node, end_node = (node1, node2) if start_node_id == node1.id else (node2, node1)
        triplet = TripletCreator.create(start_node, relation, end_node, add_stringified_triplet=False)
        return triplet
    
    def get_nodes_path(self, parent: Dict[str, str], end_node_id: str, spare_closest_node_id: str) -> List[str]:
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
        nodes_ids = [node.id for node in query_info.linked_nodes]
        #print(formated_nodes)
        unique_raw_nodes_pairs = set()
        formated_triplets = dict()

        all_pair_nodes_counter = sum(list(range(len(nodes_ids))))
        pair_nodes_counter = 0
        if len(nodes_ids) > 1:
            self.log("pair nodes calculation:", verbose=self.log_verbose)
            for i in range(len(nodes_ids)-1):
                start_node = nodes_ids[i]
                for j in range(i+1, len(nodes_ids)):
                    pair_nodes_counter += 1
                    self.log(f"{all_pair_nodes_counter} / {pair_nodes_counter}", verbose=self.log_verbose)
                    end_node = nodes_ids[j]
                    
                    s_time = time()
                    _, _, _, parent, spare_closest_node = self.graph_searcher.search_path(start_node, end_node)
                    self.log(f"search elapsed_time: {time() - s_time}", verbose=self.log_verbose)
                    
                    s_time = time()
                    nodes_path = self.get_nodes_path(parent, end_node, spare_closest_node)
                    self.log(f"get_path elapsed_time: {time() - s_time}", verbose=self.log_verbose)

                    # Сохраняем только уникальные пары вершин (по их идентификаторам)
                    s_time = time()
                    unique_raw_nodes_pairs.update([(nodes_path[i], nodes_path[i+1]) for i in range(len(nodes_path)-1)] if len(nodes_path) > 1 else [])
                    self.log(f"saving_nodes elapsed_time: {time() - s_time}", verbose=self.log_verbose)
                    
                    self.log(self.graph_searcher.metrics.cache_info, verbose=self.log_verbose)

        # Сохраняем только уникальные триплеты (по их строковым представлениям)
        self.log("pair nodes formating:", verbose=self.log_verbose)
        s_time = time()
        right_nodes_order_counter = len(unique_raw_nodes_pairs)
        for nodes_pair in unique_raw_nodes_pairs:
            triplet = self.get_formated_triplet(nodes_pair)

            # проверки на порядок нод в триплете
            if triplet.end_node.type is NodeType.object and not triplet.start_node.type is NodeType.object:
                right_nodes_order_counter -=1
            if triplet.end_node.type is NodeType.hyper and triplet.start_node.type is NodeType.episodic:
                right_nodes_order_counter -=1
            
            formated_triplets.update({triplet.id: triplet})
        
        self.log(f"triplet nodes right order: {right_nodes_order_counter} / {len(unique_raw_nodes_pairs)}", verbose=self.log_verbose)
        self.log(f"neo4j queries: {len(unique_raw_nodes_pairs)}", verbose=self.log_verbose)
        self.log(f"= sum elapsed_time: {time() - s_time}", verbose=self.log_verbose)

        return formated_triplets.values()
        