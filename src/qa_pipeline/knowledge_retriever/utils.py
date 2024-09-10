from dataclasses import dataclass
from enum import Enum
from typing import List
from abc import ABC, abstractmethod

from ..query_parser import QueryInfo

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

class AbstractTriplesFilter(ABC):
    @abstractmethod
    def apply_filter(self, query_info: QueryInfo, triplets: List[Triplet]) -> List[Triplet]:
        # фильтрация триплетов по заданному правилу
        pass

class AbstractTripletsRetriever(ABC):
    @abstractmethod
    def get_relevant_triplets(self, query_info: QueryInfo) -> List[Triplet]:
        pass
