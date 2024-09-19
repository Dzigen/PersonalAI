from dataclasses import dataclass, field
from typing import List, Union
from enum import Enum
import hashlib

class NodeType(Enum):
    object = "object"
    hyper = "hyper"
    episodic = "episodic"

NODES_TYPES_MAP = {
    'object': NodeType.object,
    'hyper': NodeType.hyper,
    'episodic': NodeType.episodic
}

class RelationType(Enum):
    simple = "simple"
    hyper = "hyper"
    episodic = "episodic"

RELATION_TYPES_MAP = {
    'simple': RelationType.simple,
    'hyper': RelationType.hyper,
    'episodic': RelationType.episodic
}

@dataclass
class Node:
    name: str
    type: str
    id: str = None
    prop: dict = field(default_factory=lambda: {})
    stringified: str = None

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
    id: str = None
    stringified: str = None

class BaseCreator:
    @staticmethod
    def add_str_props(obj: Union[Relation, Node], obj_str: str) -> str:
        str_prop = '; '.join([f"{k}: {v}" for k, v in obj.prop.items() if k not in ['name','type','raw_time']])
        if str_prop:
            obj_str += f" ({str_prop})"
        return obj_str

class NodeCreator(BaseCreator):
    @staticmethod
    def create(add_stringified_node: bool = True, **kwargs):
        node = Node(**kwargs)
        if add_stringified_node:
            _, node.stringified = NodeCreator.stringify(node)
        return node

    @staticmethod
    def stringify(node: Node) -> str:    
        return node.id, NodeCreator.add_str_props(node, node.name)

class TripletCreator(BaseCreator):
    @staticmethod
    def create(start_node: Node, relation: Relation, end_node: Node, add_stringified_triplet: bool = True) -> Triplet:
        triplet = Triplet(start_node, relation, end_node)
        _, str_triplet = TripletCreator.stringify(triplet)
        if add_stringified_triplet:
            triplet.stringified = str_triplet
        triplet.id = hashlib.md5(str_triplet.encode()).hexdigest()
        return triplet

    @staticmethod
    def stringify(triplet: Triplet) -> str:
        rel_type = triplet.relation.type
        if (rel_type == RelationType.episodic) or (rel_type == RelationType.hyper):
            str_triplet = ""
            if "time" in triplet.relation.prop.keys():
                str_triplet += triplet.relation.prop["time"] + ": "
            str_triplet += TripletCreator.add_str_props(triplet.end_node, triplet.end_node.name)
            
        elif rel_type == RelationType.simple:
            str_triplet = ""
            if "time" in triplet.relation.prop.keys():
                str_triplet += triplet.relation.prop["time"] + ": "
            str_triplet += " ".join([
                TripletCreator.add_str_props(triplet.start_node, triplet.start_node.name),
                TripletCreator.add_str_props(triplet.relation, triplet.relation.name),
                TripletCreator.add_str_props(triplet.end_node, triplet.end_node.name)])

        else:
            raise KeyError
                
        return triplet.relation.id, str_triplet


from ..embedding_functions import VectorDBInstance

@dataclass
class QueryInfo:
    query: str
    entities: List[str] = None
    linked_nodes: List[VectorDBInstance] = None