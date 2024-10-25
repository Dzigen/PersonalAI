from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import numpy as np
import heapq
from copy import deepcopy
from time import time
import collections

from .utils import AbstractTripletsRetriever
from .AStarTripletsRetriever import AStarGraphSearchConfig, AStarTripletsRetriever
from .BFSTripletsRetriever import BFSSearchConfig, BFSRetriever
from ...utils.data_structs import QueryInfo, Triplet, NodeType
from ...knowledge_graph_model import KnowledgeGraphModel
from ...utils.data_structs import create_id_for_node_pair
from ...db_drivers.kv_driver.utils import AbstractKVDatabaseConnection
from ...utils import Logger

@dataclass
class MixtureGraphSearchConfig:
    """_summary_
    """
    #
    astar_config: AStarGraphSearchConfig = field(default_factory=lambda: AStarGraphSearchConfig())
    #
    bfs_config: BFSSearchConfig = field(default_factory=lambda: BFSSearchConfig())

class MixtureTripletsRetriever(AbstractTripletsRetriever):
    def __init__(self, kg_model: KnowledgeGraphModel, log: Logger, search_config: MixtureGraphSearchConfig = MixtureGraphSearchConfig(),
                 cache: AbstractKVDatabaseConnection = None, verbose: bool = False) -> None:

        self.astar_searcher = AStarTripletsRetriever(kg_model, log, search_config.astar_config, cache, verbose)
        self.bfs_searcher = BFSRetriever(kg_model, log, search_config.bfs_config, cache, verbose)

    def get_relevant_triplets(self, query_info: QueryInfo) -> List[Triplet]:
        astar_triplets = self.astar_searcher.get_relevant_triplets(query_info)
        bfs_triplets = self.bfs_searcher.get_relevant_triplets(query_info)

        # отбираем только уникальные триплеты (по их идентификаторам)
        unique_triplets = dict()
        for triplet in astar_triplets + bfs_triplets:
            unique_triplets[triplet.id] = triplet

        return unique_triplets.values()
