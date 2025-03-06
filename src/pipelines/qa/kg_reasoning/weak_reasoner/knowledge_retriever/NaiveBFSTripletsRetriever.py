from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import numpy as np
import heapq
from time import time
import collections
from collections import Counter
from copy import deepcopy

from .utils import AbstractTripletsRetriever, BaseGraphSearchConfig

from ......utils.data_structs import QueryInfo, Triplet, NodeType
from ......kg_model import KnowledgeGraphModel
from ......utils.data_structs import create_id
from ......utils import Logger

@dataclass
class NaiveBFSGraphSearchConfig(BaseGraphSearchConfig):
    max_depth: int = 10
    max_width: int = 50
    max_passed_nodes: int = 1000
    accepted_node_types: List[NodeType] = field(default_factory=lambda:[NodeType.object , NodeType.hyper, NodeType.episodic, NodeType.time])

class NaiveBFSTripletsRetriever(AbstractTripletsRetriever):
    def __init__(self, kg_model: KnowledgeGraphModel, log: Logger, search_config: NaiveBFSGraphSearchConfig = NaiveBFSGraphSearchConfig(),
                 verbose: bool = False) -> None:
        self.log = log
        self.verbose = verbose
        self.kg_model = kg_model
        self.config = search_config

    def search(self, node_id: str) -> List[Triplet]:
        traversed_triplets = []
        visited, queue = set(), collections.deque([node_id])
        visited.add(node_id)
        D = {node_id: 0}
        parent = {node_id: None}
        neo4j_queries_counter, passed_nodes_counter = 0, 0
        max_pnodes_flag = False
        while queue:
            if max_pnodes_flag:
                break

            vertex = queue.popleft()

            if self.config.max_depth >= 0 and D[vertex] >= self.config.max_depth:
                # ограничиваем глубину обхода
                continue

            neighbours = self.kg_model.graph_struct.db_conn.get_adjecent_nids(vertex, self.config.accepted_node_types)
            neo4j_queries_counter += 1

            if self.config.max_width >= 0:
                # Ограничиваем ширину обхода
                neighbours = neighbours[:self.config.max_width]

            for neighbour in neighbours:

                if neighbour == parent[vertex]:
                    # пропускаем вершину, из которой пришли
                    continue

                if self.config.max_passed_nodes >= 0 and passed_nodes_counter >= self.config.max_passed_nodes:
                    # Ограничиваем количество вершин, которое можно обойти
                    max_pnodes_flag = True
                    break

                if neighbour not in visited:
                    passed_nodes_counter += 1
                    parent[neighbour] = vertex
                    D[neighbour] = D[vertex] + 1
                    visited.add(neighbour)

                    traversed_triplets += self.kg_model.graph_struct.db_conn.get_triplets(vertex, neighbour)
                    neo4j_queries_counter += 1
                    queue.append(neighbour)

        self.log(f"bfs graph-db queries: {neo4j_queries_counter}", verbose=self.verbose)
        self.log(f"passed nodes counter: {passed_nodes_counter}", verbose=self.verbose)

        return traversed_triplets

    def get_relevant_triplets(self, query_info: QueryInfo) -> List[Triplet]:
        self.log("START KNOWLEDGE RETRIEVING ...", verbose=self.verbose)
        self.log(f"BASE_QUESTION ID: {create_id(query_info.query)}", verbose=self.verbose)
        self.log(f"BASE_QUESTION: {query_info.query}", verbose=self.verbose)

        node_ids = set([node.id for node in query_info.linked_nodes])
        self.log(f"Вершины, для которых будет запущейн BFS: {node_ids}", verbose=self.verbose)

        unique_triplets = dict()
        for node_id in node_ids:
            self.log(f"Запускаем BFS по вершине с id: {node_id}", verbose=self.verbose)
            tmp_triplets = self.search(node_id)
            self.log(f"Количество извлечённых триплетов для данной вершины: {len(tmp_triplets)}", verbose=self.verbose)
            unique_triplets.update({triplet.relation.id: triplet for triplet in tmp_triplets})

        self.log(f"Суммарное количество уникальных (по строковому представлению) извлечённых триплетов: {len(unique_triplets)}", verbose=self.verbose)
        self.log(f"Распределение типов связей в наборе извлечённых триплетов: {Counter([triplet.relation.type for triplet in unique_triplets.values()])}", verbose=self.verbose)

        return list(unique_triplets.values())
