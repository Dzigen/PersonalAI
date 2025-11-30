from typing import Dict, List, Union
from dataclasses import dataclass, field
from abc import abstractmethod
from copy import deepcopy

from ...utils.data_structs import Triplet, NodeType, RelationType, Node, NodeInfo, RelationInfo
from ..utils import AbstractDatabaseConnection, BaseDatabaseConfig


@dataclass
class GraphDBConnectionConfig(BaseDatabaseConfig):
    """Конфигурация подключения к графовой базе данных.

    :param db_info: Информация о базе и таблице/пространстве хранения графа. По умолчанию {'db': 'DefaultPersonalAIGraphDB', 'table': 'DefaultPersonalAIGraphTable'}.
    :type db_info: Dict
    :param host: Хост, на котором развёрнута графовая БД.
    :type host: str
    :param port: Порт, по которому производится подключение к графовой БД.
    :type port: str
    """
    db_info: Dict = field(default_factory=lambda: {'db': 'DefaultPersonalAIGraphDB', 'table': 'DefaultPersonalAIGraphTable'})
    host: str = None
    port: str = None

    def to_str(self):
        str_hostport = f"{self.host};{self.port}"
        str_needto = f"{self.need_to_clear};{self.create_index}"
        return f"{self.db_info};{str_hostport};{str_needto};{self.params}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = GraphDBConnectionConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config


class AbstractGraphDatabaseConnection(AbstractDatabaseConnection):
    """Абстрактный интерфейс для взаимодействия с графовой базой данных.

    Определяет набор операций для:
     - создания триплетов,
     - получения соседних вершин,
     - получения триплетов по идентификаторам и именам,
     - получения статистики по элементам графа.
    """
    @abstractmethod
    def create(self, triplets: List[Triplet], creation_info: Dict = dict()) -> None:
        pass

    @abstractmethod
    def get_adjecent_nodes(self, base_node: NodeInfo, accepted_n_types: List[NodeType] = [NodeType.object, NodeType.hyper, NodeType.episodic]) -> List[NodeInfo]:
        """Метод предназначен для получения списка соседних вершин относительно заданной вершины.

        :param base_node: Информация об исходной вершине (идентификатор, тип, текст).
        :type base_node: NodeInfo
        :param accepted_n_types: Допустимые типы соседних вершин.
        :type accepted_n_types: List[NodeType]
        :return: Список соседних вершин, удовлетворяющих заданным типам.
        :rtype: List[Node]
        """
        pass

    @abstractmethod
    def get_nodes_shared_ids(self, node1: NodeInfo, node2: NodeInfo, id_type: str = 'both') -> List[Dict[str, str]]:
        """Метод предназначен для поиска общих идентификаторов, связывающих две заданные вершины.

        :param node1: Информация о первой вершине.
        :type node1: NodeInfo
        :param node2: Информация о второй вершине.
        :type node2: NodeInfo
        :param id_type: Тип идентификатора.
        :type id_type: str
        :return: Список общих идентификаторов, связывающих node1 и node2.
        :rtype: List[str]
        """
        pass

    @abstractmethod
    def get_triplets_by_name(self, subj_name: str, obj_name: str, obj_type) -> List[Triplet]:
        """Метод предназначен для получения триплетов по именам начальной и конечной вершин.

        :param subj_name: Имя начальной вершины (subj).
        :type subj_name: str
        :param obj_name: Имя конечной вершины (obj).
        :type obj_name: str
        :param obj_type: Тип конечной вершины.
        :type obj_type: NodeType
        :return: Список найденных триплетов.
        :rtype: List[Triplet]
        """
        pass

    @abstractmethod
    def get_triplets(self, node1: NodeInfo, node2: NodeInfo) -> List[Triplet]:
        """Метод предназначен для получения триплетов, связывающих две заданные вершины.

        :param node1: Информация о первой вершине.
        :type node1: NodeInfo
        :param node2: Информация о второй вершине.
        :type node2: NodeInfo
        :return: Список триплетов, в которых участвуют обе вершины.
        :rtype: List[Triplet]
        """
        pass

    @abstractmethod
    def read_by_name(self, name: str, object_type: Union[RelationType, NodeType],
                     object: str = 'triplet') -> List[Union[Triplet, Node]]:
        """Метод предназначен для получения вершин или триплетов по их имени.

        :param name: Имя искомого объекта (вершины или связи).
        :type name: str
        :param object_type: Тип объекта (RelationType или NodeType).
        :type object_type: Union[RelationType, NodeType]
        :param object: Тип возвращаемого объекта: 'triplet' или 'node'.
        :type object: str
        :return: Список найденных триплетов или вершин.
        :rtype: List[Union[Triplet, Node]]
        """
        pass

    @abstractmethod
    def count_items(self, item_id: Union[None, str, NodeInfo, RelationInfo] = None,
                    id_type: str = None, detailed: bool = False) -> Union[Dict[str, Dict[str, int]], Dict[str, int], int]:
        """Метод предназначен для получения статистики по количеству элементов в графовой БД.

        :param item_id: Идентификатор объекта, для которого требуется получить количество
            (например, конкретной вершины/связи), либо None для общей статистики.
        :type item_id: Union[None, str, NodeInfo, RelationInfo], optional
        :param id_type: Тип идентификатора.
        :type id_type: str, optional
        :param detailed: Если True, возвращается детализированная статистика, иначе агрегированное значение.
        :type detailed: bool, optional
        :return: Либо общее количество, либо с разбиением по типам.
        :rtype: Union[Dict[str, Dict[str, int]], Dict[str, int], int]
        """
        pass

    @abstractmethod
    def item_exist(self, item_id: Union[str, NodeInfo, RelationInfo], id_type: str = 'triplet') -> bool:
        """Метод предназначен для проверки существования объекта в графовой БД.

        :param item_id: Идентификатор объекта.
        :type item_id: Union[str, NodeInfo, RelationInfo]
        :param id_type: Тип идентификатора.
        :type id_type: str
        :return: True, если объект существует в БД, иначе False.
        :rtype: bool
        """
        pass
