from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from ...utils.data_structs import Triplet, NodeType

@dataclass
class GraphDBConnectionConfig:
    uri: str = None
    params: Dict = field(default_factory=lambda: dict())
    need_to_clear: bool = False

class AbstractGraphDatabaseConnection(ABC):

    @abstractmethod
    def open_connection(self) -> None:
        # открытие соединения с бд
        pass

    @abstractmethod
    def is_open(self) -> None:
        #
        pass

    @abstractmethod
    def close_connection(self) -> None:
        # закрытие соединения с бд
        pass

    @abstractmethod
    def create(self, items: List[Triplet]) -> None:
        """_summary_

        :param triplet: _description_
        :type triplet: Triplet
        """
        pass

    @abstractmethod
    def read(self, ids: List[Tuple[str,str,str]]) -> List[Triplet]:
        pass

    @abstractmethod
    def update(self, items: List[Triplet]) -> None:
        pass

    @abstractmethod
    def delete(self, ids: List[Triplet]) -> None:
        """_summary_

        :param triplet: _description_
        :type triplet: Triplet
        """
        pass

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

    @abstractmethod
    def count_items(self) -> int:
        pass

    @abstractmethod
    def clear(self) -> None:
        # Удаление содержания базы данных, которой было подключение
        pass

    def __del__(self):
        self.close_connection()
