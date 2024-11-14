from typing import List, Tuple, Dict
from collections import defaultdict
import gc
from copy import deepcopy
import joblib
import os
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
        for i, triplet in enumerate(triplets):
            cur_info = creation_info.get(i, None)

            t_id = self.generate_id()
            self.tid_triplets_index[triplet.id].append(t_id)
            self.triplets[t_id] = triplet

            r_id = self.generate_id()
            self.strid_relation_index[triplet.relation.id].append(r_id)
            self.relations[r_id] = triplet.relation

            #
            if cur_info is None or cur_info['s_node']:
                sn_ids = [self.generate_id()]
                self.strid_nodes_index[triplet.start_node.id].append(sn_ids[0])
                self.nodes[sn_ids[0]] = triplet.start_node
            else:
                sn_ids = self.strid_nodes_index[triplet.start_node.id]

            if cur_info is None or cur_info['e_node']:
                en_ids = [self.generate_id()]
                self.strid_nodes_index[triplet.end_node.id].append(en_ids[0])
                self.nodes[en_ids[0]] = triplet.end_node
            else:
                en_ids = self.strid_nodes_index[triplet.end_node.id]

            #
            for sn_id in sn_ids:
                self.edges[sn_id].append(t_id)
                for en_id in en_ids:
                    self.adjacent_nodes[sn_id].append(en_id)

            for en_id in en_ids:
                self.edges[en_id].append(t_id)
                for sn_id in sn_ids:
                    self.adjacent_nodes[en_id].append(sn_id)

    def read(self, ids: List[str]) -> List[Triplet]:
        triplets = []
        for id in ids:
            if type(id) is not str:
                raise ValueError
            tid_triplets = self.tid_triplets_index.get(id, None)
            if tid_triplets is not None:
                triplets += tid_triplets
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

        nodes = deepcopy(self.adjacent_nodes.get(base_node_id, []))
        filtered_nodes = list(filter(lambda n_id: self.items_ids[n_id].type in accepted_n_types, nodes))

        return filtered_nodes

    def get_triplets(self, node1_id: str, node2_id: str) -> List[Triplet]:
        if (type(node1_id) is not str) or (type(node2_id) is not str):
            raise ValueError

        shared_triplets_ids = set(self.edges[node1_id]).intersection(set(self.edges[node2_id]))
        triplets = list(map(lambda id: self.triplets_ids[id], shared_triplets_ids))
        return triplets

    def get_triplets_by_name(self, subj_names: List[str], obj_names: List[str], obj_type: str) -> List[Triplet]:
        triplets = []
        for triplet in self.triplets_ids.values():
            if obj_type in str(triplet.end_node.type):
                if subj_names and triplet.start_node.name in subj_names:
                    triplets.append(triplet)
                elif obj_names and triplet.end_node.name in obj_names:
                    triplets.append(triplet)
        return triplets

    def count_items(self) -> int:
        return {'triplets': len(self.triplets), 'nodes': len(self.nodes)}

    def item_exist(self, id: str, id_type='triplet') -> bool:
        if type(id) is not str:
            raise ValueError

        output = None
        if id_type == 'node':
            output = self.strid_nodes_index.get(id, [])
        if id_type == 'relation':
            output = self.strid_relation_index.get(id, [])
        elif id_type == 'triplet':
            output = self.tid_triplets_index.get(id, [])
        else:
            raise ValueError

        return len(output) > 0

    def clear(self) -> None:
        self.close_connection()
        self.open_connection()
        gc.collect()
