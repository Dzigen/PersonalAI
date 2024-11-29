from typing import List, Tuple, Dict
import ast

from ....utils import ReturnStatus, NodeCreator, TripletCreator, NodeType
from ....utils.data_structs import Relation, RelationType, Triplet, RelationCreator

def ethesises_custom_formate(text: str, **kwargs) -> Dict[str, str]:
    if len(text) < 1:
        raise ValueError
    return {'text': text}


def ethesises_custom_parse(raw_response: str, **kwargs) -> List[Tuple[str, List[str]]]:
    """Функция предназначена для разбора результата генерации ответа LLM-агента, в рамаках задачи по извлечению
    триплетов типа "hyper" (тезисной информации) из текста на естественном языке.

    :param raw_response: Исходный ответ LLM-агента.
    :type raw_response: str
    :return: Разобранный список 'тезисных' триплетов из ответа LLM-агента.
    :rtype: List[Tuple[str, str]]
    """
    if len(raw_response) < 1:
        raise ValueError

    if ":" in raw_response:
        raw_response = raw_response.split(":")[-1]
    raw_response = raw_response.lower().strip('.-* ').split(".")
    raw_triplets = []
    for raw_thesis in raw_response:
        if ";" not in raw_thesis:
            raise ValueError

        raw_thesis, raw_entities = raw_thesis.split(";")
        thesis = raw_thesis.strip('.-* ')
        entities = ast.literal_eval(raw_entities.strip(''' \n'".,/'''))

        raw_triplets.append((thesis, entities))

    return raw_triplets

def ethesises_custom_postprocess(parsed_response: List[Tuple[str, List[str]]], node_prop: Dict[str, object] = dict(),
                                 rel_prop: Dict[str, object] = dict(), **kwargs) -> List[Triplet]:
    formated_triplets = []
    for triplet in parsed_response:
        thesis, entities = triplet

        if len(thesis) < 1:
            raise ValueError

        thesis_node = NodeCreator.create(name=str(thesis), n_type=NodeType.hyper, prop={**node_prop})
        thesis_rel = RelationCreator.create(name=RelationType.hyper.value, r_type=RelationType.hyper, prop={**rel_prop})
        for entity in entities:
            if len(entity) < 1:
                raise ValueError

            formated_triplets.append(TripletCreator.create(
                start_node=NodeCreator.create(name=str(entity), n_type=NodeType.object, prop={**node_prop}),
                relation=thesis_rel, end_node=thesis_node))

    return formated_triplets
