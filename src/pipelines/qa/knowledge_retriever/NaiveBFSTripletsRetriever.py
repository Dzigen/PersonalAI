from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import numpy as np
import heapq
from time import time
import collections
from copy import deepcopy

from .utils import AbstractTripletsRetriever, BaseGraphSearchConfig, get_nodes_path

from ....utils.data_structs import QueryInfo, Triplet, NodeType
from ....kg_model import KnowledgeGraphModel
from ....utils.data_structs import create_id_for_node_pair, create_id
from ....db_drivers.kv_driver.utils import KeyValueDBInstance
from ....db_drivers.kv_driver import KeyValueDriverConfig, KeyValueDriver
from ....utils import Logger

class NaiveBFSGraphSearch:
    pass
    # запускаем bfs от текущей вершины
    # ограничениями выступает глубина,ширина +
    # типы врешин по которым можно обходить граф

@dataclass
class NaiveBFSGraphSearchConfig:
    max_depth: int = 10
    max_width: int = 50
    max_passed_nodes: int = 500
    accepted_node_types: List[NodeType] = field(default_factory=lambda:[NodeType.object , NodeType.hyper, NodeType.episodic])

class NaiveBFSTripletsRetriever(AbstractTripletsRetriever):
    def __init__(self, kg_model: KnowledgeGraphModel, log: Logger, search_config: NaiveBFSGraphSearchConfig = NaiveBFSGraphSearchConfig(),
                 verbose: bool = False) -> None:
        self.log = log
        self.verbose = verbose
        self.kg_model = kg_model
        self.graph_searcher = NaiveBFSGraphSearch(kg_model, log, search_config, verbose)

    def get_relevant_triplets(self, query_info: QueryInfo) -> List[Triplet]:
        pass
        # по каждой сущности извлекаем триплеты
        # сохраням уникальные триплеты по строковым представлениям
