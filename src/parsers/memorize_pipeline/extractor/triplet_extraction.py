from typing import List, Tuple
import ast

from ....utils import ReturnStatus

def etriplets_custom_parse(raw_response: str) -> Tuple[List[Tuple[str, str, str]], ReturnStatus]:
    """Функция предназначена для разбора результата генерации ответа LLM-агента, в рамаках задачи по извлечению триплетов из текста на естественном языке.

    :param raw_response: Исходный ответ LLM-агента.
    :type raw_response: str
    :return: Разобранный список триплетов из ответа LLM-агента.
    :rtype: Tuple[List[Tuple[str, str, str]], ReturnStatus]
    """
    status = ReturnStatus.success
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

    if len(raw_triplets) == 0:
        status = ReturnStatus.bad_format

    return raw_triplets, status

def etriplets_custom_formate():
    # TODO
    pass

def etriplets_custom_postprocess(self, parsed_response: str, lang: str, node_prop: Dict, rel_prop: Dict) -> Tuple[List[Triplet], ReturnStatus]:
    formated_triplets = []
    for triplet in raw_triplets:
        subj, rel, obj = triplet
        formated_triplets.append(TripletCreator.create(
            NodeCreator.create(name=str(subj), n_type=NodeType.object, prop={**node_prop}),
            Relation(name=str(rel), type=RelationType.simple, prop={**rel_prop}),
            NodeCreator.create(name=str(obj), n_type=NodeType.object, prop={**node_prop})))

    return formated_triplets, status
