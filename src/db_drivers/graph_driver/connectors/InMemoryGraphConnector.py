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
        self.items_ids = {}
        self.triplets_ids = {}

    def close_connection(self) -> None:
        del self.edges
        del self.adjacent_nodes
        del self.items_ids
        del self.triplets_ids
        gc.collect()

    def generate_id(self, seed: str = None):
        return hashlib.md5((str(time()) if seed is None else seed).encode()).hexdigest()

    def create_triplet(self, triplet: Triplet) -> None:
        created_nodes_count, created_rels_count = 0, 0
        
        #
        s_node_content_id = self.generate_id(f"{triplet.start_node.type.value} {triplet.start_node.name}")
        if s_node_content_id in self.uniques_content_nodes:
            triplet.start_node.id = self.uniques_content_nodes[s_node_content_id]
        else:
            triplet.start_node.id = self.generate_id()
            self.uniques_content_nodes[s_node_content_id] = triplet.start_node.id 

        #
        e_node_content_id = self.generate_id(f"{triplet.end_node.type.value} {triplet.end_node.name}")
        if e_node_content_id in self.uniques_content_nodes:
            triplet.end_node.id = self.uniques_content_nodes[e_node_content_id]
        else:
            triplet.end_node.id = self.generate_id()
            self.uniques_content_nodes[e_node_content_id] = triplet.end_node.id 

        triplet.relation.id = self.generate_id()
        
        self.edges[triplet.start_node.id].append(triplet.id)
        self.edges[triplet.end_node.id].append(triplet.id)
        self.adjacent_nodes[triplet.start_node.id].append(triplet.end_node.id)
        self.adjacent_nodes[triplet.end_node.id].append(triplet.start_node.id)

        self.items_ids[triplet.start_node.id] = triplet.start_node
        self.items_ids[triplet.end_node.id] = triplet.end_node
        self.triplets_ids[triplet.id] = triplet

        return created_nodes_count, created_rels_count

    def delete_triplet(self, triplet: Triplet) -> None:
        
        if triplet.id in self.triplets_ids:
            self.triplets_ids.pop(triplet.id)

            if triplet.start_node.id in self.edges:
                if triplet.id in self.edges[triplet.start_node.id]:
                    self.edges[triplet.start_node.id].remove(triplet.id)
                if not self.edges[triplet.start_node.id]:
                    self.items_ids.pop(triplet.start_node.id)
                    self.edges.pop(triplet.start_node.id)

            if triplet.end_node.id in self.edges:
                if triplet.id in self.edges[triplet.end_node.id]:
                    self.edges[triplet.end_node.id].remove(triplet.id)
                if not self.edges[triplet.end_node.id]:
                    self.items_ids.pop(triplet.end_node.id)
                    self.edges.pop(triplet.end_node.id)

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
        shared_triplets_ids = set(self.edges[node1_id]).union(set(self.edges[node2_id]))
        triplets = list(map(lambda id: self.triplets_ids[id], shared_triplets_ids))
        return triplets

    def get_triplets_by_name(self, subj_name, obj_name, obj_type):
        triplets = []
        for triplet in self.triplets_ids.values():
            if obj_type in str(triplet.end_node.type):
                if subj_name and triplet.start_node.name in subj_name:
                    triplets.append(triplet)
                elif obj_name and triplet.end_node.name in obj_name:
                    triplets.append(triplet)
        return triplets

    def __del__(self):
        self.close_connection()