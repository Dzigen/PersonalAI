from typing import Dict, List, Union
from dataclasses import dataclass, field
from abc import abstractmethod

from ...utils.data_structs import Triplet, NodeType, RelationType, Node, NodeInfo, RelationInfo
from ..utils import AbstractDatabaseConnection, BaseDatabaseConfig


@dataclass
class GraphDBConnectionConfig(BaseDatabaseConfig):
    db_info: Dict = field(default_factory=lambda: {
                          'db': 'DefaultPersonalAIGraphDB', 'table': 'DefaultPersonalAIGraphTable'})
    host: str = None
    port: str = None


class AbstractGraphDatabaseConnection(AbstractDatabaseConnection):

    @abstractmethod
    def create(self, triplets: List[Triplet], creation_info: Dict = dict()) -> None:
        pass

    @abstractmethod
    def get_adjecent_nodes(self, base_node: NodeInfo, accepted_n_types: List[NodeType] = [NodeType.object, NodeType.hyper, NodeType.episodic]) -> List[NodeInfo]:
        pass

    @abstractmethod
    def get_nodes_shared_ids(self, node1: NodeInfo, node2: NodeInfo, id_type: str = 'both') -> List[Dict[str, str]]:
        pass

    @abstractmethod
    def get_triplets_by_name(self, subj_name: str, obj_name: str, obj_type) -> List[Triplet]:
        pass

    @abstractmethod
    def get_triplets(self, node1: NodeInfo, node2: NodeInfo) -> List[Triplet]:
        pass

    @abstractmethod
    def read_by_name(self, name: str, object_type: Union[RelationType, NodeType],
                     object: str = 'triplet') -> List[Union[Triplet, Node]]:
        pass

    @abstractmethod
    def count_items(self, item_id: Union[None, str, NodeInfo, RelationInfo] = None, 
                    id_type: str = None, detailed: bool = False) -> Union[Dict[str, Dict[str, int]], Dict[str, int], int]:
        pass

    @abstractmethod
    def item_exist(self, item_id: Union[str, NodeInfo, RelationInfo], id_type: str = 'triplet') -> bool:
        pass
