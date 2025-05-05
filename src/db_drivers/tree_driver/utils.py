from typing import Dict, List, Union
from dataclasses import dataclass, field, asdict
from abc import abstractmethod
from enum import Enum

from ...utils import ReturnInfo
from ...utils.data_structs import Triplet, NodeType, RelationType, Node
from ..utils import AbstractDatabaseConnection, BaseDatabaseConfig

class TreeNodeType(Enum):
    leaf = "leaf"
    root = "root"
    summarized = "summarized"

@dataclass
class TreeNode:
    id: str
    text: str
    type: TreeNodeType
    props: Dict[str, object]

@dataclass
class TreeDBConnectionConfig(BaseDatabaseConfig):
    host: str = None
    port: str = None

class AbstractTreeDatabaseConnection(AbstractDatabaseConnection):

    root_node_id: str = "ROOT_NODE"

    @abstractmethod
    def create(self, parent_id: str, new_node: TreeNode) -> None:
        pass

    @abstractmethod
    def read(self, ids: List[str], type: str = 'leaf') -> List[TreeNode]:
        pass

    @abstractmethod
    def update(self, items: List[TreeNode]) -> None:
        pass

    @abstractmethod
    def delete(self, ids: List[str], type: str = 'leaf') -> None:
        pass

    @abstractmethod
    def item_exist(self, id: str, type: str = 'leaf') -> bool:
        pass

    @abstractmethod
    def get_child_nodes(parent_id: str) -> List[TreeNode]:
        pass
