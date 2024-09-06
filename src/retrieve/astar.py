from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import joblib
import numpy as np
import hashlib

from ..knowledge_graph_model import KnowledgeGraphModel
from ..qa_pipeline.query_parser.utils import QueryInfo
from ..qa_pipeline.knowledge_retriever.utils import Node, Relation, Triplet

@dataclass
class AStarMetricsConfig:
    h_metric_name: str = 'weight_with_short_path'
    d_metric_name: str = 'ip'
    nodes_distances_path: str = '../../data/nodes_distances'
    nodes_short_paths_file: str = '../../data/nodes_short_paths'

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

    def compute_d_metric(self, *args, **kwargs):
        return self.metrics_map[self.config.d_metric_name](*args, **kwargs)

    def compute_h_metric(self, *args, **kwargs):
        return self.metrics_map[self.config.h_metric_name](*args, **kwargs)

    def get_nodes_path(self, parent, U, end_node, spare_closest_node):
        if end_node['id'] not in parent.keys():
            node = spare_closest_node
        else:
            node = end_node  
        
        path, end_flag, cur_n = [node], False, node['id']
        while not end_flag:
            next_n = parent[cur_n]
            if next_n is None:
                end_flag = True
            else:
                path.append(U[next_n])
                cur_n = next_n

        return path

    def precomputed_dist(self, node1, node2, U, parent):
        return self.nodes_dists['MATRIX'][self.nodes_dists['ID_TO_INDEX_MAP'][node1['id']]][self.nodes_dists['ID_TO_INDEX_MAP'][node2['id']]]
        
    def weighted_short_path(self, node1, node2, U, parent):
        short_dist = self.nodes_short_paths['MATRIX'][self.nodes_short_paths['ID_TO_INDEX_MAP'][node1['id']]][self.nodes_short_paths['ID_TO_INDEX_MAP'][node2['id']]]
        w = self.precomputed_dist(node1, node2, U, parent)
        return short_dist * w

    def avg_weighted_short_path(self, node1, node2, U, parent):
        nodes_path = self.get_nodes_path(parent, U, node1, None)
        acc_dist = 0
        for i in range(len(nodes_path)-1):
            acc_dist += self.precomputed_dist(nodes_path[i], nodes_path[i+1], U, parent)
        acc_dist += self.precomputed_dist(node1, node2, U, parent)

        short_dist = self.nodes_short_paths['MATRIX'][self.nodes_short_paths['ID_TO_INDEX_MAP'][node1['id']]][self.nodes_short_paths['ID_TO_INDEX_MAP'][node2['id']]]
        return np.mean(acc_dist) * short_dist 

class AStarGraphSearchConfig:
    max_depth: int = 10 
    max_width: int = -1
    graphdb_name: str = 'testdb'
    accepted_node_types: List[str] = '["object", "hyper", "episodic"]'
    metrics_config: AStarMetricsConfig = AStarMetricsConfig()

class AStarGraphSearch:
    def __init__(self, kg_model: KnowledgeGraphModel, 
                 search_config: AStarGraphSearchConfig = None) -> None:
        self.config = AStarGraphSearchConfig() if search_config is None else search_config
        self.kg_model = kg_model
        self.metrics = AStarMetrics(config=self.config.metrics_config)

    def get_adjecent_nodes(self, base_node, parent) -> List[Dict]:
        raw_nodes = self.kg_model.graph_db.execute_query(
            f'MATCH (a)-[r]-(b) WHERE elementId(a) = "{base_node["id"]}" AND ANY (node_t IN b.type WHERE node_t IN {self.config.accepted_node_types}) RETURN b', 
            db=self.config.graphdb_name)
        formated_nodes = list({node['b'].element_id: {'id': node['b'].element_id, 'name': node['b']['name']} for node in raw_nodes 
                            if node['b'].element_id != parent[base_node['id']]}.values())

        return formated_nodes

    def filter_adjenced_nodes(base_node, adj_nodes, distance_metric, U, parent, max_width: int = 10):
        sorted_adj_n_distances = sorted(list(map(lambda node_item: (node_item[0], distance_metric(base_node, node_item[1], U, parent)), enumerate(adj_nodes))), 
                                        key=lambda item: item[1])
        filtered_nodes = [adj_nodes[item[0]] for item in sorted_adj_n_distances[:max_width]]

        return filtered_nodes

    def get_min_f_node(self, Q: Dict, f: Dict) -> Dict:
        node_ids = list(Q.keys())
        min_node_id = node_ids[0]
        min_f = f[min_node_id]

        for idx in range(1, len(node_ids)):
            if f[node_ids[idx]] < min_f:
                min_node_id = node_ids[idx]
                min_f = f[min_node_id]
                
        return Q[min_node_id]

    def search_path(self, start_node: Dict, end_node: Dict):
        U, Q, D = {}, {start_node['id']: start_node}, {start_node['id']: 0}
        g = {start_node['id']: 0}
        parent = {start_node['id']: None}
        f = {start_node['id']: g[start_node['id']] + self.metrics.compute_h_metric(start_node, end_node, U, parent)}
        
        spare_closest_node = start_node
        while len(Q) != 0:

            current = self.get_min_f_node(Q, f) # вершина из Q с минимальным значением f

            # Сохраняем промежуточную вершину, до которой есть путь. 
            # Если не будет найден путь до end_node, то будет использован путь до spare_closest_node
            if self.metrics.compute_h_metric(current, end_node, U, parent) <= self.metrics.compute_h_metric(spare_closest_node, end_node, U, parent):
                if f[current['id']] <= f[spare_closest_node['id']]:
                    spare_closest_node = current
            
            #
            if current['id'] == end_node['id']:
                break

            del Q[current['id']]
            if D[current['id']] >= self.config.max_depth:
                continue
            U[current['id']] = current

            adj_nodes = self.get_adjecent_nodes(current, parent)

            if self.config.max_width > 0:
                adj_nodes = self.filter_adjenced_nodes(
                    current, adj_nodes, U, parent)

            break_flag = False
            for v in adj_nodes:
                tentativeScore = g[current['id']] + self.metrics.compute_d_metric(current, v, U, parent)      
                if (v['id'] in U.keys()) and (tentativeScore >= g[v['id']]):
                    continue
                if (v['id'] not in U.keys()) or (tentativeScore < g[v['id']]):
                    parent[v['id']] = current['id']
                    g[v['id']] = tentativeScore
                    f[v['id']] = g[v['id']] + self.metrics.compute_d_metric(v, end_node, U, parent)
                    D[v['id']] = D[current['id']] + 1

                    if v['id'] not in Q.keys():
                        Q[v['id']] = v

            if break_flag:
                break

        return U, Q, D, parent, spare_closest_node
    
class AStartTripletsRetriever(AStarGraphSearch):
    def __init__(self, kg_model: KnowledgeGraphModel, search_config: AStarGraphSearchConfig = None) -> None:
        super().__init__(kg_model, search_config)

    def get_path_tripletes(self, nodes_path: List[Dict]) -> Dict[str, Triplet]:
        tripletes = {}
        for i in range(len(nodes_path)-1):
            node1, node2 = nodes_path[i], nodes_path[i+1]
            relations = self.kg_model.graph_db.execute_query(
                f'MATCH (n1)-[rel]-(n2) WHERE elementId(n1) = "{node1["id"]}" AND elementId(n2) = "{node2["id"]}"  RETURN n1, rel, n2, (startNode(rel) = n1) as n1_is_start_node',
                db=self.config.graphdb_name)
                
            for relation in relations:
                formated_node1 = Node(name=relation['n1']['name'], type=list(relation['n1'].labels)[0],
                                      id=relation['n1'].element_id, prop=relation['n1'])
                formated_node2 = Node(name=relation['n2']['name'], type=list(relation['n2'].labels)[0], 
                                      id=relation['n2'].element_id, prop=relation['n2'])
                formated_relation = Relation(type=relation['rel'].type, id=relation['rel'].element_id,
                                             prop=relation['rel'])
                s_node, e_node = (formated_node1, formated_node2) if relation['n1_is_start_node'] else (formated_node2, formated_node1) 
                tripletes[formated_relation.id] = Triplet(start_node=s_node, relation=formated_relation, end_node=e_node)

        return tripletes
    
    def get_nodes_path(parent, U, end_node, spare_closest_node):
        if end_node['id'] not in parent.keys():
            node = spare_closest_node
        else:
            node = end_node  
        
        path, end_flag, cur_n = [node], False, node['id']
        while not end_flag:
            next_n = parent[cur_n]
            if next_n is None:
                end_flag = True
            else:
                path.append(U[next_n])
                cur_n = next_n

        return path

    def get_relevant_triplets(self, query_info: QueryInfo):
        formated_nodes = [{'id': node.id, 'name': node.document} for node in query_info.linked_nodes]
        tripletes_pool = dict()
        if len(formated_nodes) > 1:
            for i in range(len(formated_nodes)-1):
                start_node = formated_nodes[i]
                for j in range(i+1, len(formated_nodes)):
                    end_node = formated_nodes[j]
                    U, _, _, parent, spare_closest_node = self.search_path(start_node, end_node)
                    nodes_path = self.get_nodes_path(parent, U, end_node, spare_closest_node)
                    new_tripletes = self.get_path_tripletes(nodes_path) # сразу формируется уникальный (по содержанию) набор триплетов

                    tripletes_pool.update(new_tripletes)

        return list(tripletes_pool.values())
        