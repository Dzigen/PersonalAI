from typing import List, Tuple, Dict

from ......utils import NodeCreator, TripletCreator, NodeType
from ......utils.data_structs import RelationType, Triplet, RelationCreator


def ethesises_custom_formate(text: str, **kwargs) -> Dict[str, str]:
    """Функция формирует словарь контекста для LLM-задачи по извлечению тезисов.

    :param text: Исходный текст на естественном языке.
    :type text: str
    :return: Словарь с полем 'text', передаваемый в LLM-подзадачу.
    :rtype: Dict[str, str]
    """
    if len(text) < 1:
        raise ValueError
    return {'text': text}


def ethesises_custom_postprocess(parsed_response: List[Tuple[str, List[str]]], node_prop: Dict[str, object] = dict(),
                                 rel_prop: Dict[str, object] = dict(), **kwargs) -> List[Triplet]:
    """Функция предназначена для постобработки разобранного ответа LLM-агента в задаче извлечения тезисной информации.

    :param parsed_response: Результат парсинга ответа LLM-агента, список пар (тезис, список связанных сущностей).
    :type parsed_response: List[Tuple[str, List[str]]]
    :param node_prop: Дополнительные свойства, которые будут добавлены к создаваемым вершинам. Значение по умолчанию dict().
    :type node_prop: Dict[str, object], optional
    :param rel_prop: Дополнительные свойства, которые будут добавлены к создаваемым рёбрам. Значение по умолчанию dict().
    :type rel_prop: Dict[str, object], optional
    :return: Список триплетов с типом связи 'hyper'.
    :rtype: List[Triplet]
    """
    formated_triplets = []
    for triplet in parsed_response:
        thesis, entities = triplet

        if len(thesis) < 1:
            raise ValueError(f"parsed_response: '{parsed_response}'")

        thesis_node = NodeCreator.create(
            name=str(thesis), n_type=NodeType.hyper, prop={**node_prop})
        thesis_rel = RelationCreator.create(
            name=RelationType.hyper.value, r_type=RelationType.hyper, prop={**rel_prop})
        for entity in entities:
            if len(entity) < 1:
                raise ValueError(f"parsed_response: '{parsed_response}'")

            formated_triplets.append(TripletCreator.create(
                start_node=NodeCreator.create(
                    name=str(entity), n_type=NodeType.object, prop={**node_prop}),
                relation=thesis_rel, end_node=thesis_node))

    return formated_triplets
