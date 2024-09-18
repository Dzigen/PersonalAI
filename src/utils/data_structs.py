from dataclasses import dataclass, field
from typing import List

@dataclass
class Node:
    name: str
    type: str
    id: str = None
    prop: dict = field(default_factory=lambda: {})

@dataclass
class Relation:
    name: str
    type: str
    id: str = None
    prop: dict = field(default_factory=lambda: {})

@dataclass
class Triplet:
    start_node: Node 
    relation: Relation 
    end_node: Node

from ..embedding_functions import VectorDBInstance

@dataclass
class QueryInfo:
    query: str
    entities: List[str] = None
    linked_nodes: List[VectorDBInstance] = None