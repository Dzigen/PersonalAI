from dataclasses import dataclass
from enum import Enum
from ...retrieve.astar import AStarGraphSearch

class GraphSearchMethod(Enum):
    astar = AStarGraphSearch

class TripletsFilterMethod(Enum):
    embeddings_distance = 'embeddings_distance'

@dataclass
class KnowledgeRetrieverConfig:
    graph_search_method: object
    graph_search_config: object
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
    prop: dict

@dataclass
class Triplet:
    start_node: Node 
    relation: Relation 
    end_node: Node