from typing import Dict, List
from dataclasses import dataclass, field
from abc import abstractmethod

from ...utils import ReturnInfo
from ...utils.data_structs import Triplet, NodeType
from ..utils import AbstractDatabaseConnection, BaseDatabaseConfig

@dataclass
class GraphDBConnectionConfig(BaseDatabaseConfig):
    uri: str = None

class AbstractGraphDatabaseConnection(AbstractDatabaseConnection):

    @abstractmethod
    def create(self, triplets: List[object], creation_info: Dict = dict()) -> ReturnInfo:
        pass

    @abstractmethod
    def get_adjecent_nodes(self, base_node_id: str, accepted_n_types: List[NodeType]) -> List[str]:
        pass

    @abstractmethod
    def get_triplets_by_name(self, subj_name: str, obj_name: str, obj_type) -> List[Triplet]:
        pass

    @abstractmethod
    def get_triplets(self, node1_id: str, node2_id: str) -> List[Triplet]:
        pass
