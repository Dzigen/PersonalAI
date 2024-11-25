from typing import List, Tuple, Dict
import ast

from ....utils import ReturnStatus, NodeCreator, TripletCreator, NodeType
from ....utils.data_structs import Relation, RelationType, Triplet

def etriplets_custom_formate(text: str, node_prop: Dict[str, object] = dict(),
                             rel_prop: Dict[str, object] = dict()) -> Dict[str, str]:
    # TODO
    return dict()

def etriplets_custom_parse(raw_response: str, **kwargs) -> List[Tuple[str, str, str]]:
    """Функция предназначена для разбора ответа LLM-агента, полученного в рамаках задачи по извлечению триплетов из текста на естественном языке.

    :param raw_response: Исходный ответ LLM-агента.
    :type raw_response: str
    :return: Разобранный список триплетов из ответа LLM-агента.
    :rtype: List[Tuple[str, str, str]]
    """
    if ":" in raw_response:
        raw_response = raw_response.split(":")[-1]
    raw_response = raw_response.lower()
    raw_response = raw_response.split(";")
    raw_triplets = []
    for triplet in raw_response:
        if len(triplet.split(",")) != 3:
            continue
        subj, rel, obj = triplet.split(",")
        subj, rel, obj = subj.split(":")[-1].split(".")[-1].strip(''' \n'".,/'''), rel.strip(''' \n'".,/'''), obj.strip(''' \n'".,/''')
        if len(subj) == 0 or len(rel) == 0 or len(obj) == 0:
            continue
        else:
            raw_triplets.append((subj, rel, obj))

    return raw_triplets

def etriplets_custom_postprocess(parsed_response: List[Tuple[str, str, str]],  node_prop: Dict[str, object] = dict(),
                                 rel_prop: Dict[str, object] = dict(), **kwargs) -> List[Triplet]:
    formated_triplets = []
    for triplet in parsed_response:
        subj, rel, obj = triplet
        formated_triplets.append(TripletCreator.create(
            NodeCreator.create(name=str(subj), n_type=NodeType.object, prop={**node_prop}),
            Relation(name=str(rel), type=RelationType.simple, prop={**rel_prop}),
            NodeCreator.create(name=str(obj), n_type=NodeType.object, prop={**node_prop})))

    return formated_triplets
