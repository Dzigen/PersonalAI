from dataclasses import dataclass, field
from typing import List, Union
from enum import Enum
import hashlib

class NodeType(Enum):
    """Доступные типы вершин."""
    #: Вершина хранить атомарную сущность.
    object = "object"
    #: Вершина хранит тезисную информацию.
    hyper = "hyper"
    #: Вершина хранит эпизодическую информацию.
    episodic = "episodic"

NODES_TYPES_MAP = {
    'object': NodeType.object,
    'hyper': NodeType.hyper,
    'episodic': NodeType.episodic
}

class RelationType(Enum):
    """Доступные типы связей/триплетов."""
    #: Связывает только вершины с типом 'object'.
    simple = "simple"
    #: Связывает пары вершин ('object','hyper').
    hyper = "hyper"
    #: Связывает пары вершин ('object', 'episodic') и ('object', 'hyper').
    episodic = "episodic"

RELATIONS_TYPES_MAP = {
    'simple': RelationType.simple,
    'hyper': RelationType.hyper,
    'episodic': RelationType.episodic
}

@dataclass
class Node:
    #: Основное хранилище информации.
    name: str
    #: Тип вершины
    type: NodeType
    #: Дополнительные свойства вершины
    prop: dict = field(default_factory=lambda: {})
    #: Строковое представление вершины
    stringified: str = None
    #: Идентификатор вершины, полученный на основе её стрококового представления.
    id: str = None

@dataclass
class Relation:
    #: Основное хранилище информации.
    name: str
    # Тип связи.
    type: RelationType
    #: Дополнительные свойства вершины
    prop: dict = field(default_factory=lambda: {})
    #: Идентификатор триплета, полученный на основе его стрококового представления.
    #: Отличается от значения в поле id объекта класса Triplet.
    id: str = None

@dataclass
class Triplet:
    #
    start_node: Node
    #
    relation: Relation
    #
    end_node: Node
    #: Строковое представление триплета
    stringified: str = None
    #: Идентификатор триплета, полученный на основе его стрококового представления.
    #: Отличается от значения в поле id объекта класса Relation.
    id: str = None

class BaseCreator:
    @staticmethod
    def add_str_props(obj: Union[Relation, Node], obj_str: str) -> str:
        """Метод предназначен для добавления свойств, хранящихся в структуре связи/вершины, к их базовым стрококвым представлениям.

        :param obj: Структура объекта, строковое представление которого обогащается его свойствами.
        :type obj: Union[Relation, Node]
        :param obj_str: Текущее стрококове представление объекта.
        :type obj_str: str
        :return: Обогащённое строковое представление.
        :rtype: str
        """
        str_prop = '; '.join([f"{k}: {v}" for k, v in obj.prop.items() if k not in ['name', 'type', 'raw_time', 'time', 'str_id', 't_id']])
        if str_prop:
            obj_str += f" ({str_prop})"
        return obj_str

class NodeCreator(BaseCreator):
    @staticmethod
    def create(add_stringified_node: bool = True, **kwargs) -> Node:
        """Метод предназначен для создания структуры данных вершины с указанным содержанием.

        :param add_stringified_node: Если True, то в структуру данных вершины будет сохранено её строковое представление, иначе False, defaults to True
        :type add_stringified_node: bool, optional
        :param kwargs: Значения полей структуры данных Node. Если они не будут указаны, то будут использованы значения по-умолчанию.
        :return: Созданная структура данных вершины.
        :rtype: Node
        """
        node = Node(**kwargs)
        _, str_node = NodeCreator.stringify(node)
        node.id = create_id(str_node)
        if add_stringified_node:
            node.stringified = str_node
        return node

    @staticmethod
    def stringify(node: Node) -> str:
        """Метод предназначен для приведения структуры данных вершины в её строковое представление.

        :param triplet: Структура данных вершины
        :type triplet: Node
        :return: Стрококвое представление.
        :rtype: str
        """
        str_node = ""
        if "time" in node.prop.keys():
            str_node += node.prop["time"] + ": "
        str_node += NodeCreator.add_str_props(node, str(node.name))
        return node.id, str_node

def create_id_for_node_pair(node1_id: str, node2_id: str) -> str:
    """Метод предназначен для условной генерации идентификатора к паре вершин. Вершины представлены в виде их собственных идентификаторов.
    При указании такой же пары вершин, но в другом порядке, полученный идентифкатор не изменится: инвариант относительно перестановок.

    :param node1_id: Идентификатор первой веришины.
    :type node1_id: str
    :param node2_id: Идентификатор второй вешины.
    :type node2_id: str
    :return: Идентификатор пары вершин.
    :rtype: str
    """
    start_id, end_id = (node1_id, node2_id) if node1_id > node2_id else (node2_id, node1_id)
    return hashlib.md5((start_id+end_id).encode()).hexdigest()

def create_id(seed: str) -> str:
    return hashlib.md5(seed.encode()).hexdigest()

class TripletCreator(BaseCreator):
    @staticmethod
    def create(start_node: Node, relation: Relation, end_node: Node,
            add_stringified_triplet: bool = True, t_id: str = None) -> Triplet:
        """Метод предназначен для создания структуры данных триплета с указанным содержанием.
        Триплет является ориентированным: у связи между вершинами (парой объект/субъект) есть направление.

        :param start_node: Структура данных старотовой вершины триплета
        :type start_node: Node
        :param relation: Структура данных связи триплета.
        :type relation: Relation
        :param end_node: Структура данных конеченой вершины триплета.
        :type end_node: Node
        :param add_stringified_triplet: Если True, то в структуру данных триплета будет сохранено его строковое представление, иначе False, defaults to True
        :type add_stringified_triplet: bool, optional
        :param t_id: Идентификатор триплета, который будет назначен вручную, defaults to None. Если идентификатор не указан, то он будет автоматически сгенерирован.
        :type t_id: str, optional
        :return: Созданная структура данных триплета.
        :rtype: Triplet
        """

        triplet = Triplet(start_node, relation, end_node)
        _, str_triplet = TripletCreator.stringify(triplet)
        if add_stringified_triplet:
            triplet.stringified = str_triplet
        triplet.relation.id = create_id(str_triplet)

        if t_id is None:
            triplet.id = create_id(''.join(
                [triplet.start_node.id,triplet.relation.id,triplet.end_node.id]))
        else:
            triplet.id = t_id

        return triplet

    @staticmethod
    def stringify(triplet: Triplet) -> str:
        """Метод предназначен для приведения структуры данных триплета в его строковое представление. Строковое представление зависит от типа триплета:
        (1) simple - используется информация из обоих вершин и связи; (2) hyper/episodic - используется информация только из конечной вершины.

        :param triplet: Структура данных триплета
        :type triplet: Triplet
        :raises KeyError: В триплете указа связь с типом, который не поддерживается.
        :return: Стрококвое представление.
        :rtype: str
        """
        rel_type = triplet.relation.type
        if (rel_type == RelationType.episodic) or (rel_type == RelationType.hyper):
            str_triplet = ""
            if "time" in triplet.end_node.prop.keys():
                str_triplet += triplet.end_node.prop["time"] + ": "
            str_triplet += TripletCreator.add_str_props(triplet.end_node, str(triplet.end_node.name))

        elif rel_type == RelationType.simple:
            str_triplet = ""
            if "time" in triplet.relation.prop.keys():
                str_triplet += triplet.relation.prop["time"] + ": "
            str_triplet += " ".join([
                TripletCreator.add_str_props(triplet.start_node, str(triplet.start_node.name)),
                TripletCreator.add_str_props(triplet.relation, str(triplet.relation.name)),
                TripletCreator.add_str_props(triplet.end_node, str(triplet.end_node.name))])

        else:
            raise KeyError

        return triplet.relation.id, str_triplet


#from ..embedding_functions import VectorDBInstance

@dataclass
class QueryInfo:
    """Класс предназначен для хранения промежуточных результатов по user-вопросу,
    который обрабатывается в рамках QA-конвейера
    """
    #: Исходный user-вопрос.
    query: str
    #: Набор сущностей, который был извлечён из user-вопроса.
    entities: List[str] = None
    #: Набор объектов (вершин) из памяти (графа знаний) ассистента,
    #: который был сопоставлен сущностям из user-вопроса.
    linked_nodes: List[object] = None
    linked_nodes_by_entities: List[object] = None
