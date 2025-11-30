from typing import List, Tuple, Dict

from ......utils import NodeCreator, TripletCreator, NodeType
from ......utils.data_structs import RelationType, Triplet, RelationCreator


def etriplets_custom_formate(text: str, **kwargs) -> Dict[str, str]:
    """Функция формирует словарь контекста для LLM-задачи по извлечению триплетов.

    :param text: Исходный текст на естественном языке.
    :type text: str
    :return: Словарь с полем 'text', передаваемый в LLM-подзадачу.
    :rtype: Dict[str, str]
    """
    if len(text) < 1:
        raise ValueError

    return {'text': text}


def etriplets_custom_postprocess(parsed_response: List[Tuple[str, str, str]], node_prop: Dict[str, object] = dict(),
                                 rel_prop: Dict[str, object] = dict(), **kwargs) -> List[Triplet]:
    """Функция предназначена для постобработки разобранного ответа LLM-агента в задаче извлечения триплетов.

    :param parsed_response: Результат парсинга ответа LLM-агента, список триплетов в формате (субъект, отношение, объект).
    :type parsed_response: List[Tuple[str, str, str]]
    :param node_prop: Дополнительные свойства, которые будут добавлены к создаваемым вершинам. Значение по умолчанию dict().
    :type node_prop: Dict[str, object], optional
    :param rel_prop: Дополнительные свойства, которые будут добавлены к создаваемым рёбрам. Значение по умолчанию dict().
    :type rel_prop: Dict[str, object], optional
    :return: Список триплетов с типом связи 'simple'.
    :rtype: List[Triplet]
    """
    formated_triplets = []
    for triplet in parsed_response:
        subj, rel, obj = triplet

        if len(subj) < 1 or len(rel) < 1 or len(obj) < 1:
            raise ValueError(f"parsed_response: '{parsed_response}'")

        formated_triplets.append(TripletCreator.create(
            start_node=NodeCreator.create(
                name=subj, n_type=NodeType.object, prop={**node_prop}),
            relation=RelationCreator.create(
                name=rel, r_type=RelationType.simple, prop={**rel_prop}),
            end_node=NodeCreator.create(name=obj, n_type=NodeType.object, prop={**node_prop})))

    return formated_triplets
