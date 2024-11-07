from typing import Dict, List
from dataclasses import dataclass, field
from abc import abstractmethod

from ...utils.data_structs import Triplet, NodeType
from ..utils import AbstractDatabaseConnection

@dataclass
class GraphDBConnectionConfig:
    uri: str = None
    params: Dict = field(default_factory=lambda: dict())
    need_to_clear: bool = False

class AbstractGraphDatabaseConnection(AbstractDatabaseConnection):

    @abstractmethod
    def get_adjecent_nodes(self, base_node_id: str, parent_node_id: str, accepted_n_types: List[NodeType]) -> List[str]:
        """_summary_

        :param base_node_id: _description_
        :type base_node_id: str
        :param parent_node_id: _description_
        :type parent_node_id: str
        :param accepted_n_types: _description_
        :type accepted_n_types: List[NodeType]
        :return: _description_
        :rtype: List[str]
        """
        pass

    @abstractmethod
    def get_triplets_by_name(self, subj_name: str, obj_name: str, obj_type) -> List[Triplet]:
        pass

    @abstractmethod
    def get_all_triplets_between_nodes(self, node1_id: str, node2_id: str) -> List[Triplet]:
        """_summary_

        :param node1_id: _description_
        :type node1_id: str
        :param node2_id: _description_
        :type node2_id: str
        :return: _description_
        :rtype: List[Triplet]
        """
        pass
