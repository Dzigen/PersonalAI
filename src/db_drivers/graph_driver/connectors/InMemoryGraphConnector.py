from typing import List, Dict
from collections import defaultdict
import gc
from time import time
import hashlib

from ..utils import GraphDBConnectionConfig, AbstractGraphDatabaseConnection
from ....utils import Triplet, NodeType

DEFAULT_INMEMORYGRAPH_CONFIG = GraphDBConnectionConfig()

class InMemoryGraphConnector(AbstractGraphDatabaseConnection):
    """_summary_"""

    def __init__(self, config: GraphDBConnectionConfig) -> None:
        self.config = config
        self.open_connection()

    def open_connection(self) -> None:
        self.edges = defaultdict(list)
        self.adjacent_nodes = defaultdict(list)

        self.nodes = defaultdict(list)
        self.relations = defaultdict(list)
        self.triplets = defaultdict(list)

        self.strid_relation_index = defaultdict(list)
        self.strid_nodes_index = defaultdict(list)
        self.tid_triplets_index = defaultdict(list)

    def is_open(self) -> bool:
        need_to_exist = [
            'edges', 'adjacent_nodes', 'nodes', 'relations', 'triplets',
            'strid_nodes_index', 'str_relation_index', 'tid_triplets_index']
        condition = True
        for field in need_to_exist:
            condition = condition and hasattr(self, field)
        return condition

    def close_connection(self) -> None:
        del self.edges
        del self.adjacent_nodes

        del self.nodes
        del self.relations
        del self.triplets

        del self.strid_nodes_index
        del self.strid_relation_index
        del self.tid_triplets_index
        gc.collect()

    def generate_id(self, seed: str = None):
        return hashlib.md5((str(time()) if seed is None else seed).encode()).hexdigest()

    def create(self, triplets: List[Triplet], creation_info: Dict = dict()) -> None:
        # triplet-ids checking
        for triplet in triplets:
            if type(triplet.id) is not str:
                raise ValueError
        unique_ids = set(map(lambda triplet: triplet.id, triplets))
        if len(triplets) != len(unique_ids):
            raise ValueError

        for i, triplet in enumerate(triplets):
            cur_info = creation_info.get(i, None)

            #
            if cur_info is None or cur_info['s_node']:
                new_node_id = self.generate_id()
                print("n1: ", triplet.start_node.id)
                self.strid_nodes_index[triplet.start_node.id].append(new_node_id)
                self.nodes[new_node_id] = triplet.start_node

            if cur_info is None or cur_info['e_node']:
                new_node_id = self.generate_id()
                print("n2: ", triplet.end_node.id)
                self.strid_nodes_index[triplet.end_node.id].append(new_node_id)
                self.nodes[new_node_id] = triplet.end_node

            sn_ids = self.strid_nodes_index[triplet.start_node.id]
            en_ids = self.strid_nodes_index[triplet.end_node.id]

            # NOTE: если в графе будет несколько вершин с одинаковым str_id,
            # то нам необходимо их все соединить ребром с новой вершиной
            # например:
            # - есть два триплета (n1, rel1, n2) и (n2, rel2, n3) c пустой creation_info (пусть номера это str_id)
            # - сначала стандартно полностью добавляем первый трипет
            # - при добавлении второго триплета у нас вершина n2 в граф добавляется повторно с другим внутренним id (из-за пустого creation_info)
            # - таким образом добавленную в граф вершину n3 нужно связать с вершиной n2 как из второго так и их первого триплетов
            for sn_id in sn_ids:
                for en_id in en_ids:
                    t_id = self.generate_id()
                    self.tid_triplets_index[triplet.id].append(t_id)
                    self.triplets[t_id] = triplet

                    r_id = self.generate_id()
                    self.strid_relation_index[triplet.relation.id].append(r_id)
                    self.relations[r_id] = triplet.relation

                    self.edges[sn_id].append(t_id)
                    if en_id not in self.adjacent_nodes[sn_id]:
                        self.adjacent_nodes[sn_id].append(en_id)

                    self.edges[en_id].append(t_id)
                    if sn_id not in self.adjacent_nodes[en_id]:
                        self.adjacent_nodes[en_id].append(sn_id)


    def read(self, ids: List[str]) -> List[Triplet]:
        triplets = []
        for id in ids:
            if type(id) is not str:
                raise ValueError
            t_ids = self.tid_triplets_index.get(id, None)
            if t_ids is not None:
                triplets += list(map(lambda t_id: self.triplets[t_id], t_ids))
        return triplets

    def update(self, items: List[Triplet]) -> None:
        # TODO
        pass

    def delete(self, ids: List[str]) -> None:
        # TODO
        pass

    def get_adjecent_nodes(self, base_node_id: str, accepted_n_types: List[NodeType]) -> List[str]:
        if type(base_node_id) is not str:
            raise ValueError

        node_db_ids = self.strid_nodes_index.get(base_node_id, [])
        adjanced_nodes_db_ids = []
        for node_id in node_db_ids:
            adjanced_nodes_db_ids += self.adjacent_nodes[node_id]

        filtered_adj_n_dbids = list(filter(lambda n_db_id: self.nodes[n_db_id].type in accepted_n_types, adjanced_nodes_db_ids))
        nodes_str_ids = list(map(lambda db_n_id: self.nodes[db_n_id].id, filtered_adj_n_dbids))
        return nodes_str_ids

    def get_triplets(self, node1_id: str, node2_id: str) -> List[Triplet]:
        if (type(node1_id) is not str) or (type(node2_id) is not str):
            raise ValueError

        start_n_db_ids = self.strid_nodes_index.get(node1_id, None)
        if start_n_db_ids is None:
            raise ValueError
        start_n_edges = []
        for n_db_id in start_n_db_ids:
            start_n_edges += self.edges[n_db_id]

        end_n_db_ids = self.strid_nodes_index.get(node2_id, None)
        if end_n_db_ids is None:
            raise ValueError
        end_n_edges = []
        for n_db_id in end_n_db_ids:
            end_n_edges += self.edges[n_db_id]

        shared_triplets_ids = set(end_n_edges).intersection(set(start_n_edges))
        triplets = list(map(lambda id: self.triplets[id], shared_triplets_ids))
        return triplets

    def get_triplets_by_name(self, subj_names: List[str], obj_names: List[str], obj_type: str) -> List[Triplet]:
        triplets = []
        for triplet in self.triplets.values():
            if obj_type in str(triplet.end_node.type):
                if subj_names and triplet.start_node.name in subj_names:
                    triplets.append(triplet)
                elif obj_names and triplet.end_node.name in obj_names:
                    triplets.append(triplet)
        return triplets

    def count_items(self) -> int:
        return {'triplets': len(self.triplets), 'nodes': len(self.nodes)}

    def item_exist(self, item_id: str, id_type: str ='triplet') -> bool:
        if type(item_id) is not str:
            raise ValueError

        output = None
        if id_type == 'node':
            output = self.strid_nodes_index.get(item_id, [])
        elif id_type == 'relation':
            output = self.strid_relation_index.get(item_id, [])
        elif id_type == 'triplet':
            output = self.tid_triplets_index.get(item_id, [])
        else:
            raise ValueError

        return len(output) > 0

    def clear(self) -> None:
        self.close_connection()
        self.open_connection()
        gc.collect()
