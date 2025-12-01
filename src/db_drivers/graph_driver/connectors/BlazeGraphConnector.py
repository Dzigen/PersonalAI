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
        raise NotImplementedError

    def open_connection(self) -> None:
        # TODO
        raise NotImplementedError

    def close_connection(self) -> None:
        # TODO
        raise NotImplementedError

    def __del__(self):
        self.close_connection()

    def is_open(self) -> bool:
        # TODO
        raise NotImplementedError

    def create_node_query(self, node: Node) -> str:
        # TODO
        raise NotImplementedError

    def create_rel_query(self, triplet: Triplet) -> str:
        # TODO
        raise NotImplementedError

    def create(self, triplets: List[Triplet], creation_info: Dict[int, Dict[str, bool]] = dict()) -> ReturnInfo:
        # TODO
        raise NotImplementedError

    def read(self, ids: List[str]) -> List[Triplet]:
        # TODO
        raise NotImplementedError

    def update(self, items: List[Triplet]) -> ReturnInfo:
        # TODO
        raise NotImplementedError

    def delete(self, ids: List[str], delete_info: Dict[int, Dict[str, bool]] = dict()) -> None:
        # TODO
        raise NotImplementedError

    def read_by_name(self, name: str, object_type: Union[RelationType, NodeType], object: str = 'relation') -> List[Union[Triplet, Node]]:
        # TODO
        raise NotImplementedError

    def parse_query_nodes_output(self, output: QueryResult) -> List[Node]:
        # TODO
        raise NotImplementedError

    def parse_query_triplets_output(self, output: QueryResult) -> List[Triplet]:
        # TODO
        raise NotImplementedError

    def get_adjecent_nodes(self, base_node: NodeInfo,
                           accepted_n_types: List[NodeType] = [NodeType.object, NodeType.hyper, NodeType.episodic]) -> List[NodeInfo]:
        # TODO
        raise NotImplementedError

    def get_nodes_shared_ids(self, node1: NodeInfo, node2: NodeInfo, id_type: str = 'both') -> List[Dict[str, str]]:
        # TODO
        raise NotImplementedError

    def get_triplets_by_name(self, subj_names: List[str], obj_names: List[str], obj_type: str) -> List[Triplet]:
        # TODO
        raise NotImplementedError

    def get_triplets(self, node1: NodeInfo, node2: NodeInfo) -> List[Triplet]:
        # TODO
        raise NotImplementedError

    def count_items(self, item_id: Union[None, str, NodeInfo, RelationInfo] = None,
                    id_type: str = None, detailed: bool = False) -> Union[Dict[str, Dict[str, int]], Dict[str, int], int]:
        # TODO
        raise NotImplementedError

    def item_exist(self, item_id: Union[str, NodeInfo, RelationInfo], id_type: str = 'triplet') -> bool:
        # TODO
        raise NotImplementedError

    def clear(self) -> None:
        # TODO
        raise NotImplementedError
