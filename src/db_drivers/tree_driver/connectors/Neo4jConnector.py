from typing import List, Dict, Tuple

from ..utils import AbstractTreeDatabaseConnection, TreeDBConnectionConfig, TreeNode

DEFAULT_NEO4JTREE_CONFIG = ...

class Neo4jTreeConnector(AbstractTreeDatabaseConnection):

    def __init__(self, config: TreeDBConnectionConfig = DEFAULT_NEO4JTREE_CONFIG):
        self.config = config

    def open_connection(self) -> None:
        # подключение к бд
        # создание структуры таблицы
        # индексирование
        pass

    def is_open(self) -> bool:
        pass

    def close_connection(self) -> None:
        pass

    def create(self, parent_id: str, new_node: TreeNode) -> None:
        pass

    def read(self, ids: List[str], type: str = 'leaf') -> List[TreeNode]:
        pass

    def update(self, items: List[TreeNode]) -> None:
        pass

    def delete(self, ids: List[str], type: str = 'leaf') -> None:
        pass

    def count_items(self) -> Dict[str, int]:
        pass

    def item_exist(self, id: str, type: str = 'leaf') -> bool:
        pass

    def clear(self) -> None:
        pass

    def get_child_nodes(parent_id: str) -> List[TreeNode]:
        pass
