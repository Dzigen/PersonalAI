from dataclasses import dataclass, field
from typing import List, Union
from enum import Enum
import hashlib

class NodeType(Enum):
    """_summary_"""
    object = "object"
    hyper = "hyper"
    episodic = "episodic"

NODES_TYPES_MAP = {
    'object': NodeType.object,
    'hyper': NodeType.hyper,
    'episodic': NodeType.episodic
}

class RelationType(Enum):
    """_summary_"""
    simple = "simple"
    hyper = "hyper"
    episodic = "episodic"

RELATIONS_TYPES_MAP = {
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
        str_prop = '; '.join([f"{k}: {v}" for k, v in obj.prop.items() if k not in ['name', 'type', 'raw_time', 'time', 'str_id', 't_id']])
        if str_prop:
            obj_str += f" ({str_prop})"
        return obj_str

class NodeCreator(BaseCreator):
    @staticmethod
    def create(add_stringified_node: bool = True, **kwargs):
        node = Node(**kwargs)
        _, str_node = NodeCreator.stringify(node)
        node.id = create_id(str_node)
        if add_stringified_node:
            node.stringified = str_node
        return node

    @staticmethod
    def stringify(node: Node) -> str:
        str_node = ""
        if "time" in node.prop.keys():
            str_node += node.prop["time"] + ": "
        str_node += NodeCreator.add_str_props(node, str(node.name))
        return node.id, str_node

def create_id_for_node_pair(node1_id: str, node2_id: str) -> str:
    start_id, end_id = (node1_id, node2_id) if node1_id > node2_id else (node2_id, node1_id)
    return hashlib.md5((start_id+end_id).encode()).hexdigest()

def create_id(seed: str) -> str:
    return hashlib.md5(seed.encode()).hexdigest()

class TripletCreator(BaseCreator):
    @staticmethod
    def create(
            start_node: Node,
            relation: Relation,
            end_node: Node,
            add_stringified_triplet: bool = True,
            t_id: str = None
        ) -> Triplet:
        triplet = Triplet(start_node, relation, end_node)
        _, str_triplet = TripletCreator.stringify(triplet)
        if add_stringified_triplet:
            triplet.stringified = str_triplet
        triplet.relation.id = create_id(str_triplet)

        if t_id is None:
            triplet.id = create_id(''.join(
                [triplet.start_node.id,triplet.relation.id,triplet.end_node.id]))
        else:
            triplet.id = t_id

        return triplet

    @staticmethod
    def stringify(triplet: Triplet) -> str:
        rel_type = triplet.relation.type
        if (rel_type == RelationType.episodic) or (rel_type == RelationType.hyper):
            str_triplet = ""
            if "time" in triplet.end_node.prop.keys():
                str_triplet += triplet.end_node.prop["time"] + ": "
            str_triplet += TripletCreator.add_str_props(triplet.end_node, str(triplet.end_node.name))

        elif rel_type == RelationType.simple:
            str_triplet = ""
            if "time" in triplet.relation.prop.keys():
                str_triplet += triplet.relation.prop["time"] + ": "
            str_triplet += " ".join([
                TripletCreator.add_str_props(triplet.start_node, str(triplet.start_node.name)),
                TripletCreator.add_str_props(triplet.relation, str(triplet.relation.name)),
                TripletCreator.add_str_props(triplet.end_node, str(triplet.end_node.name))])

        else:
            raise KeyError

        return triplet.relation.id, str_triplet


#from ..embedding_functions import VectorDBInstance

@dataclass
class QueryInfo:
    query: str
    entities: List[str] = None
    linked_nodes: List[object] = None
    linked_nodes_by_entities: List[object] = None
