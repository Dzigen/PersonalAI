from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import joblib
import numpy as np

from .utils import AbstractTripletsRetriever
from ...utils.data_structs import QueryInfo, Node, Relation, Triplet, NodeCreator, TripletCreator, NodeType
from ...knowledge_graph_model import KnowledgeGraphModel
from ...utils.data_structs import NODES_TYPES_MAP, RELATIONS_TYPES_MAP

@dataclass
class AStarMetricsConfig:
    h_metric_name: str = 'weight_with_short_path'
    d_metric_name: str = 'ip'
    nodes_distances_path: str = '../data/vectorized_nodes/v8/nodes_distances_matrix'
    nodes_short_paths_file: str = '../data/graph_short_paths/stage2/v2/distances_matrix'

@dataclass
class AStarGraphSearchConfig:
    max_depth: int = 10 
    max_width: int = -1
    graphdb_name: str = 'testdb'
    accepted_node_types: List[str] = f'["{NodeType.object.value}", "{NodeType.hyper.value}", "{NodeType.episodic.value}"]'
    metrics_config: AStarMetricsConfig = field(default_factory=lambda:AStarMetricsConfig())

class AStarMetrics:
    def __init__(self, config: AStarMetricsConfig = None) -> None:
        self.config = AStarMetricsConfig() if config is None else config
        self.metrics_map = {
            'l2': self.precomputed_dist,
            'ip': self.precomputed_dist,
            'constant': lambda v1, v2, U, parent: 1,
            'weight_with_short_path': self.weighted_short_path,
            'avg_weighted_with_short_path': self.avg_weighted_short_path,
        }

        self.nodes_dists = joblib.load(self.config.nodes_distances_path)
        self.nodes_short_paths = joblib.load(self.config.nodes_short_paths_file)

    def compute_d_metric(self, *args, **kwargs) -> float:
        return self.metrics_map[self.config.d_metric_name](*args, **kwargs)

    def compute_h_metric(self, *args, **kwargs) -> float:
        return self.metrics_map[self.config.h_metric_name](*args, **kwargs)

    def get_nodes_path(parent: Dict[str, str], end_node_id: str, spare_closest_node_id: str) -> List[str]:
        end_node_id = spare_closest_node_id if end_node_id not in parent else end_node_id
        
        path, end_flag, cur_n = [end_node_id], False, end_node_id
        while not end_flag:
            next_n = parent[cur_n]
            if next_n is None:
                end_flag = True
            else:
                path.append(next_n)
                cur_n = next_n

        return path

    def precomputed_dist(self, node1_id: str, node2_id: str, U: List[str], parent: Dict[str, str]) -> float:
        return self.nodes_dists['MATRIX'][self.nodes_dists['ID_TO_INDEX_MAP'][node1_id]][self.nodes_dists['ID_TO_INDEX_MAP'][node2_id]]
        
    def weighted_short_path(self, node1_id: str, node2_id: str, U: List[str], parent: Dict[str, str]) -> float:
        short_dist = self.nodes_short_paths['MATRIX'][self.nodes_short_paths['ID_TO_INDEX_MAP'][node1_id]][self.nodes_short_paths['ID_TO_INDEX_MAP'][node2_id]]
        w = self.precomputed_dist(node1_id, node2_id, U, parent)
        return short_dist * w

    def avg_weighted_short_path(self, node1_id: str, node2_id: str, U: List[str], parent: Dict[str, str]) -> float:
        nodes_path = self.get_nodes_path(parent, U, node1_id, None)
        acc_dist = 0
        for i in range(len(nodes_path)-1):
            acc_dist += self.precomputed_dist(nodes_path[i], nodes_path[i+1], U, parent)
        acc_dist += self.precomputed_dist(node1_id, node2_id, U, parent)

        short_dist = self.nodes_short_paths['MATRIX'][self.nodes_short_paths['ID_TO_INDEX_MAP'][node1_id]][self.nodes_short_paths['ID_TO_INDEX_MAP'][node2_id]]
        return np.mean(acc_dist) * short_dist 

class AStarGraphSearch:
    """Класс с реализацией A*-алгоритма поиска по графу"""

    def __init__(self, kg_model: KnowledgeGraphModel, 
                 search_config: AStarGraphSearchConfig = None) -> None:
        self.config = AStarGraphSearchConfig() if search_config is None else search_config
        self.kg_model = kg_model
        self.metrics = AStarMetrics(config=self.config.metrics_config)

    def get_adjecent_nodes(self, base_node_id: str, parent: Dict[str, str]) -> List[str]:
        raw_nodes = self.kg_model.graph_db.execute_query(
            f'MATCH (a)-[r]-(b) WHERE elementId(a) = "{base_node_id}" AND ANY(lbl in {self.config.accepted_node_types} where lbl in labels(b)) RETURN b')
        formated_nodes = [node['b'].element_id for node in raw_nodes if node['b'].element_id != parent[base_node_id]]
        
        return formated_nodes

    def filter_adjenced_nodes(base_node_id: str, adj_nodes_ids: List[str], distance_metric, U: List[str], parent: Dict[str, str], max_width: int = 10) -> List[Dict]:
        sorted_adj_n_distances = sorted(list(map(lambda node_item: (node_item[0], distance_metric(base_node_id, node_item[1], U, parent)), enumerate(adj_nodes_ids))), 
                                        key=lambda item: item[1])
        filtered_nodes = [adj_nodes_ids[item[0]] for item in sorted_adj_n_distances[:max_width]]

        return filtered_nodes

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
        while len(Q) != 0:

            current_node_id, current_node_idx = self.get_min_f_node(Q, f) # вершина из Q с минимальным значением f

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

            adj_nodes = self.get_adjecent_nodes(current_node_id, parent)

            if self.config.max_width > 0:
                adj_nodes = self.filter_adjenced_nodes(
                    current_node_id, adj_nodes, U, parent)

            break_flag = False
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

            if break_flag:
                break

        return U, Q, D, parent, spare_closest_node_id
    
class AStartTripletsRetriever(AStarGraphSearch, AbstractTripletsRetriever):
    """Главный класс для извлечения триплетов из графа знаний, релевантных запросу, на основе A*-алгоритма поиска.

    Args:
        AStarGraphSearch: A* алгоритм поиска по графу знаний.
        AbstractTripletsRetriever: Интерфейс для классов с алгоритма извлечения релевантных триплетов из графов знаний.
    """
    
    def __init__(self, kg_model: KnowledgeGraphModel, search_config: AStarGraphSearchConfig = None) -> None:
        super().__init__(kg_model, search_config)

    def get_path_triplets(self, nodes_ids_path: List[str]) -> Dict[str, Triplet]:
        formated_triplets = {}
        for i in range(len(nodes_ids_path)-1):
            node1_id, node2_id = nodes_ids_path[i], nodes_ids_path[i+1]
            raw_triplets = self.kg_model.graph_db.execute_query(
                f'MATCH (n1)-[rel]->(n2) WHERE elementId(n1) = "{node1_id}" AND elementId(n2) = "{node2_id}" RETURN n1, rel, n2')
                
            for raw_triplet in raw_triplets:
                start_node = NodeCreator.create(id=raw_triplet['n1'].element_id, name=raw_triplet['n1']['name'], 
                                                type=NODES_TYPES_MAP[list(raw_triplet['n1'].labels)[0]],
                                                prop=dict(raw_triplet['n1']))
                end_node = NodeCreator.create(id=raw_triplet['n2'].element_id, name=raw_triplet['n2']['name'], 
                                              type=NODES_TYPES_MAP[list(raw_triplet['n2'].labels)[0]],
                                              prop=dict(raw_triplet['n2']))
                relation = Relation(id=raw_triplet['rel'].element_id, name=raw_triplet['rel']['name'], 
                                    type=RELATIONS_TYPES_MAP[raw_triplet['rel'].type], 
                                    prop=dict(raw_triplet['rel']))
                
                triplet = TripletCreator.create(start_node, relation, end_node, add_stringified_triplet=False)
                formated_triplets[triplet.id] = triplet

        return formated_triplets
    
    def get_nodes_path(self, parent: Dict[str, str], end_node_id: str, spare_closest_node_id: str) -> List[str]:
        end_node_id = spare_closest_node_id if end_node_id not in parent else end_node_id
        
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
        formated_nodes = [node.id for node in query_info.linked_nodes]
        tripletes_pool = dict()
        if len(formated_nodes) > 1:
            for i in range(len(formated_nodes)-1):
                start_node = formated_nodes[i]
                for j in range(i+1, len(formated_nodes)):
                    end_node = formated_nodes[j]
                    _, _, _, parent, spare_closest_node = self.search_path(start_node, end_node)
                    nodes_path = self.get_nodes_path(parent, end_node, spare_closest_node)
                    new_tripletes = self.get_path_triplets(nodes_path) # сразу формируется уникальный (по идентификаторам триплетов) набор триплетов

                    tripletes_pool.update(new_tripletes)

        return list(tripletes_pool.values())
        