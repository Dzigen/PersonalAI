from dataclasses import dataclass
from enum import Enum
from ...retrieve.astar import AStartTripletsRetriever

class GraphRetrieveMethod(Enum):
    astar = AStartTripletsRetriever

class TripletsFilterMethod(Enum):
    embeddings_distance = 'embeddings_distance'

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
    type: str
    prop: dict

@dataclass
class Triplet:
    start_node: Node 
    relation: Relation 
    end_node: Node