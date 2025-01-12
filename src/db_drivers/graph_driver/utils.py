from typing import Dict, List, Union
from dataclasses import dataclass
from abc import abstractmethod

from ...utils import ReturnInfo
from ...utils.data_structs import Triplet, NodeType, RelationType, Node
from ..utils import AbstractDatabaseConnection, BaseDatabaseConfig

@dataclass
class GraphDBConnectionConfig(BaseDatabaseConfig):
    uri: str = None

class AbstractGraphDatabaseConnection(AbstractDatabaseConnection):

    @abstractmethod
    def create(self, triplets: List[Triplet], creation_info: Dict = dict()) -> ReturnInfo:
        """_summary_

        :param triplets: _description_
        :type triplets: List[Triplet]
        :param creation_info: _description_, defaults to dict()
        :type creation_info: Dict, optional
        :return: _description_
        :rtype: ReturnInfo
        """

    @abstractmethod
    def get_adjecent_nodes(self, base_node_id: str, accepted_n_types: List[NodeType] = [NodeType.object, NodeType.hyper, NodeType.episodic]) -> List[str]:
        """_summary_

        :param base_node_id: _description_
        :type base_node_id: str
        :param accepted_n_types: _description_, defaults to [NodeType.object, NodeType.hyper, NodeType.episodic]
        :type accepted_n_types: List[NodeType], optional
        :return: _description_
        :rtype: List[str]
        """

    @abstractmethod
    def get_triplets_by_name(self, subj_name: str, obj_name: str, obj_type) -> List[Triplet]:
        """_summary_

        :param subj_name: _description_
        :type subj_name: str
        :param obj_name: _description_
        :type obj_name: str
        :param obj_type: _description_
        :type obj_type: _type_
        :return: _description_
        :rtype: List[Triplet]
        """

    @abstractmethod
    def get_triplets(self, node1_id: str, node2_id: str) -> List[Triplet]:
        """_summary_

        :param node1_id: _description_
        :type node1_id: str
        :param node2_id: _description_
        :type node2_id: str
        :return: _description_
        :rtype: List[Triplet]
        """

    @abstractmethod
    def read_by_name(self, name: str, type: Union[RelationType,NodeType],
                     object: str = 'triplet') -> List[Union[Triplet, Node]]:
        """_summary_

        :param name: _description_
        :type name: str
        :param type: _description_
        :type type: Union[RelationType,NodeType]
        :param object: _description_, defaults to 'triplet'
        :type object: str, optional
        :return: _description_
        :rtype: List[Union[Triplet, Node]]
        """

    @abstractmethod
    def count_items(self, id: str = None, id_type: str = None) -> Union[Dict[str,int],int]:
        """_summary_

        :param id: _description_, defaults to None
        :type id: str, optional
        :param id_type: _description_, defaults to None
        :type id_type: str, optional
        :return: _description_
        :rtype: Union[Dict[str,int],int]
        """

    @abstractmethod
    def item_exist(self, id: str, id_type: str='triplet') -> bool:
        """_summary_

        :param id: _description_
        :type id: str
        :param id_type: _description_, defaults to 'triplet'
        :type id_type: str, optional
        :return: _description_
        :rtype: bool
        """
