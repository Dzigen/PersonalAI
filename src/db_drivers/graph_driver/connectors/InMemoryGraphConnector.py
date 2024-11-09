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
    def __init__(self, config: GraphDBConnectionConfig) -> None:
        self.config = config
        self.open_connection()

    def open_connection(self) -> None:
        self.edges = defaultdict(list)
        self.adjacent_nodes = defaultdict(list)
        self.uniques_content_nodes = defaultdict(list)
        self.unique_content_relations = defaultdict(list)

        self.items_ids = {}
        self.triplets_ids = {}

    def is_open(self) -> bool:
        # TODO
        pass

    def close_connection(self) -> None:
        del self.edges
        del self.adjacent_nodes
        del self.items_ids
        del self.triplets_ids
        gc.collect()

    def generate_id(self, seed: str = None):
        return hashlib.md5((str(time()) if seed is None else seed).encode()).hexdigest()

    def create(self, triplets: List[Triplet], creation_info: Dict = dict()) -> None:
        created_nodes_count, created_rels_count = 0, 0
        for i, triplet in enumerate(triplets):
            cur_info = creation_info.get(i, None)

            if cur_info is None or cur_info['s_node']:
                self.items_ids[triplet.start_node.id] = triplet.start_node
            if cur_info is None or cur_info['e_node']:
                self.items_ids[triplet.end_node.id] = triplet.end_node

            if cur_info is None or cur_info['rel']:
                self.edges[triplet.start_node.id].append(triplet.id)
                self.edges[triplet.end_node.id].append(triplet.id)
                self.adjacent_nodes[triplet.start_node.id].append(triplet.end_node.id)
                self.adjacent_nodes[triplet.end_node.id].append(triplet.start_node.id)

            self.triplets_ids[triplet.id] = triplet

        return created_nodes_count, created_rels_count

    def read(self, ids: List[str]) -> List[Triplet]:
        # TODO
        pass

    def update(self, items: List[Triplet]) -> None:
        # TODO
        pass

    def delete(self, ids: List[str]) -> None:
        # TODO
        pass

    def get_adjecent_nodes(self, base_node_id: str, parent_node_id: str, accepted_n_types: List[NodeType]) -> List[str]:
        nodes = deepcopy(self.adjacent_nodes.get(base_node_id, []))
        filtered_nodes = list(filter(lambda n_id: self.items_ids[n_id].type in accepted_n_types, nodes))

        try:
            parent_idx = filtered_nodes.index(parent_node_id)
            del nodes[parent_idx]
        except ValueError:
            pass

        return filtered_nodes

    def get_triplets(self, node1_id: str, node2_id: str) -> List[Triplet]:
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
        return len(self.triplets_ids)

    def item_exist(self, id: str) -> bool:
        # TODO
        pass

    def clear(self) -> None:
        # TODO
        pass
