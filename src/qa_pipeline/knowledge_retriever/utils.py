from dataclasses import dataclass
from enum import Enum
from typing import List

@dataclass
class NaiveTripletsFilterConfig:
    pass

@dataclass
class AStarMetricsConfig:
    h_metric_name: str = 'weight_with_short_path'
    d_metric_name: str = 'ip'
    nodes_distances_path: str = '../../data/nodes_distances'
    nodes_short_paths_file: str = '../../data/nodes_short_paths'


class AStarGraphSearchConfig:
    max_depth: int = 10 
    max_width: int = -1
    graphdb_name: str = 'testdb'
    accepted_node_types: List[str] = '["object", "hyper", "episodic"]'
    metrics_config: AStarMetricsConfig = AStarMetricsConfig()


@dataclass
class KnowledgeRetrieverConfig:
    graph_retriever_method: object
    graph_retriever_config: object
    triplets_filter_method: object
    triplets_filter_config: object


@dataclass
class Node:
    id: str
    name: str
    type: str
    prop: dict

@dataclass
class Relation:
    id: str
    name: str
    type: str
    prop: dict

@dataclass
class Triplet:
    start_node: Node 
    relation: Relation 
    end_node: Node