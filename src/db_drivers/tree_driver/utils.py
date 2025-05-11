from typing import Dict, List
from dataclasses import dataclass
from abc import abstractmethod
from enum import Enum

from ..utils import AbstractDatabaseConnection, BaseDatabaseConfig

class TreeNodeType(Enum):
    leaf = "leaf"
    root = "root"
    summarized = "summarized"

TREENODES_TYPES_MAP = {
    'leaf': TreeNodeType.leaf,
    'root': TreeNodeType.root,
    'summarized': TreeNodeType.summarized
}


class TreeIdType(Enum):
    external = "external_id"
    str = "str_id"

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

    root_node_id: str = "ROOT_NODE_ID"

    @abstractmethod
    def check_consistency(self) -> None:
        pass

    @abstractmethod
    def create(self, parent_id: str, new_node: TreeNode) -> None:
        pass

    @abstractmethod
    def read(self, ids: List[str], ids_type: TreeIdType = TreeIdType.external) -> List[TreeNode]:
        pass

    @abstractmethod
    def update(self, items: List[TreeNode]) -> None:
        pass

    @abstractmethod
    def delete(self, ids: List[str], ids_type: TreeIdType = TreeIdType.external) -> None:
        pass

    @abstractmethod
    def item_exist(self, id: str, id_type: str = TreeIdType.external) -> bool:
        pass

    @abstractmethod
    def get_child_nodes(self, parent_id: str) -> List[TreeNode]:
        pass

    @abstractmethod
    def get_tree_maxdepth(self):
        pass
