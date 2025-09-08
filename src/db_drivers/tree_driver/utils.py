from typing import Dict, List
from dataclasses import dataclass, field
from abc import abstractmethod
from enum import Enum

from ..utils import AbstractDatabaseConnection, BaseDatabaseConfig

class TreeNodeType(Enum):
    #: Вершина, у которой нет child- и descendants- вершин.
    leaf = "leaf"
    #: Корневая вершина дерева.
    root = "root"
    # Вершина, у которой есть минимум одна child- или descendants-вершина типа 'leaf'.
    summarized = "summarized"

TREENODES_TYPES_MAP = {
    'leaf': TreeNodeType.leaf,
    'root': TreeNodeType.root,
    'summarized': TreeNodeType.summarized
}

class TreeIdType(Enum):
    #: Уникальное значение, выдаваемое каждой новой вершине для её идентификации.
    external = "external_id"
    #: Значение, полученный на основе срокового представления (значения в строковом поле) соответствующей вершины.
    str = "str_id"

@dataclass
class TreeNode:
    id: str
    text: str
    type: TreeNodeType
    props: Dict[str, object]

@dataclass
class TreeDBConnectionConfig(BaseDatabaseConfig):
    db_info: Dict = field(default_factory=lambda: {'db': 'defaultpersonalaitreedb', 'table': 'defaultpersonalaitreetable'})
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
    def get_leaf_descendants(self, ancestor_id: str, id_type: str = TreeIdType.external) -> List[TreeNode]:
        """Метод предназначен для получения всех leaf-вершин/потомков для вершины-предка с заданным ancestor_id-идентификатором.

        :param ancestor_id: Идентификатор вершины-предка.
        :type ancestor_id: str
        :param id_type: Тип идентификатора, по которому осуществляется поиск/выбор вершины-предка, Значение по умолчанию TreeIdType.external.
        :type id_type: str, optional
        :return: Список leaf-вершин, которые являются потомками заданной ancestor_id-вершины.
        :rtype: List[TreeNode]
        """
        pass

    @abstractmethod
    def get_child_nodes(self, parent_id: str, id_type: str = TreeIdType.external) -> List[TreeNode]:
        """Метод предназначен для получения всех leaf-вершин у parent-вершини с заданным id.

        :param parent_id: Идентификатор parent-вершины.
        :type parent_id: str
        :param id_type: Тип идентификатора, по которому осуществляется поиск/выбор parent-вершины, Значение по умолчанию TreeIdType.external.
        :type id_type: str, optional
        :return: Список child-вершин, принадлежаших заданной parent-вершине.
        :rtype: List[TreeNode]
        """
        pass

    @abstractmethod
    def get_tree_maxdepth(self) -> int:
        """Метод предназначен для получения глубины хранящегося дерева вершин.

        :return: Значение глубины дерева.
        :rtype: int
        """
        pass
