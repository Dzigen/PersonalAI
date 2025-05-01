from typing import Dict, List, Union
from dataclasses import dataclass
from abc import abstractmethod

from ...utils import ReturnInfo
from ...utils.data_structs import Triplet, NodeType, RelationType, Node
from ..utils import AbstractDatabaseConnection, BaseDatabaseConfig

@dataclass
class TreeDBConnectionConfig(BaseDatabaseConfig):
    host: str = None
    port: str = None

class AbstractTreeDatabaseConnection(AbstractDatabaseConnection):

    root_node_id: str = "ROOT_NODE"

    @abstractmethod
    def leaf_exist():
        pass

    @abstractmethod
    def change_node_type_to_summarized():
        pass

    @abstractmethod
    def count_items():
        pass

    @abstractmethod
    def get_child_nodes():
        pass
