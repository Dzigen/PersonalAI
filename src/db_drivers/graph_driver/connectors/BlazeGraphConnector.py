from typing import List, Dict, Union
from kuzu.query_result import QueryResult
import json
import os

from .configs import DEFAULT_BLAZE_CONFIG
from ..utils import GraphDBConnectionConfig, AbstractGraphDatabaseConnection
from ....utils.errors import ReturnInfo
from ....utils.data_structs import Node, NODES_TYPES_MAP, TripletCreator, Relation, RELATIONS_TYPES_MAP, \
    RelationType, NodeInfo, RelationInfo, from_str_to_nodeinfo, from_str_to_relationinfo
from ....utils import Triplet, NodeType


class BlazeGraphConnector(AbstractGraphDatabaseConnection):

    def __init__(self, config: Union[Dict, GraphDBConnectionConfig] = DEFAULT_BLAZE_CONFIG) -> None:
        # TODO
        pass

    def open_connection(self) -> None:
        # TODO
        pass

    def close_connection(self) -> None:
        # TODO
        pass

    def __del__(self):
        self.close_connection()

    def is_open(self) -> bool:
        # TODO
        pass

    def create_node_query(self, node: Node) -> str:
        # TODO
        pass

    def create_rel_query(self, triplet: Triplet) -> str:
        # TODO
        pass

    def create(self, triplets: List[Triplet], creation_info: Dict[int, Dict[str, bool]] = dict()) -> ReturnInfo:
        # TODO
        pass

    def read(self, ids: List[str]) -> List[Triplet]:
        # TODO
        pass

    def update(self, items: List[Triplet]) -> ReturnInfo:
        # TODO
        pass

    def delete(self, ids: List[str], delete_info: Dict[int, Dict[str, bool]] = dict()) -> None:
        # TODO
        pass

    def read_by_name(self, name: str, object_type: Union[RelationType, NodeType], object: str = 'relation') -> List[Union[Triplet, Node]]:
        # TODO
        pass

    def parse_query_nodes_output(self, output: QueryResult) -> List[Node]:
        # TODO
        pass

    def parse_query_triplets_output(self, output: QueryResult) -> List[Triplet]:
        # TODO
        pass

    def get_adjecent_nodes(self, base_node: NodeInfo,
                           accepted_n_types: List[NodeType] = [NodeType.object, NodeType.hyper, NodeType.episodic]) -> List[NodeInfo]:
        # TODO
        pass

    def get_nodes_shared_ids(self, node1: NodeInfo, node2: NodeInfo, id_type: str = 'both') -> List[Dict[str, str]]:
        # TODO
        pass

    def get_triplets_by_name(self, subj_names: List[str], obj_names: List[str], obj_type: str) -> List[Triplet]:
        # TODO
        pass

    def get_triplets(self, node1: NodeInfo, node2: NodeInfo) -> List[Triplet]:
        # TODO
        pass

    def count_items(self, item_id: Union[None, str, NodeInfo, RelationInfo] = None,
                    id_type: str = None, detailed: bool = False) -> Union[Dict[str, Dict[str, int]], Dict[str, int], int]:
        # TODO
        pass

    def item_exist(self, item_id: Union[str, NodeInfo, RelationInfo], id_type: str = 'triplet') -> bool:
        # TODO
        pass

    def clear(self) -> None:
        # TODO
        pass
