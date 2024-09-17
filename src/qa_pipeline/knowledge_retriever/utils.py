from dataclasses import dataclass, field
from enum import Enum
from typing import List
from abc import ABC, abstractmethod

from ..query_parser import QueryInfo

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

class AbstractTriplesFilter(ABC):
    @abstractmethod
    def apply_filter(self, query_info: QueryInfo, triplets: List[Triplet]) -> List[Triplet]:
        # фильтрация триплетов по заданному правилу
        pass

class AbstractTripletsRetriever(ABC):
    @abstractmethod
    def get_relevant_triplets(self, query_info: QueryInfo) -> List[Triplet]:
        # извлечение триплетов из графа знаний, релевантных запросу
        pass
