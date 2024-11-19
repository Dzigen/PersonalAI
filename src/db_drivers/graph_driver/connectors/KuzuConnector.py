from typing import List, Dict
from collections import defaultdict
import gc
from time import time
import hashlib

from ....utils.errors import ReturnInfo

from ..utils import GraphDBConnectionConfig, AbstractGraphDatabaseConnection
from ....utils import Triplet, NodeType

DEFAULT_KUZU_CONFIG = GraphDBConnectionConfig()

class KuzuConnector(AbstractGraphDatabaseConnection):

    def open_connection(self) -> ReturnInfo:
        # TODO
        pass

    def close_connection(self) -> ReturnInfo:
        # TODO
        pass

    def create(self, items: List[object]) -> ReturnInfo:
        # TODO
        pass

    def read(self, ids: List[str]) -> List[object]:
        # TODO
        pass

    def update(self, items: List[object]) -> ReturnInfo:
        # TODO
        pass

    def delete(self, ids: List[str]) -> ReturnInfo:
        # TODO
        pass

    def get_adjecent_nodes(self, base_node_id: str, parent_node_id: str, accepted_n_types: List[NodeType]) -> List[str]:
        # TODO
        pass

    def get_triplets_by_name(self, subj_name: str, obj_name: str, obj_type) -> List[Triplet]:
        # TODO
        pass

    def get_triplets(self, node1_id: str, node2_id: str) -> List[Triplet]:
        # TODO
        pass
