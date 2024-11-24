from typing import List, Tuple
import ast

from ....utils import ReturnStatus

def ethesises_custom_parse(raw_response: str) -> Tuple[List[Tuple[str, str]], ReturnStatus]:
    """Функция предназначена для разбора результата генерации ответа LLM-агента, в рамаках задачи по извлечению тезисной информации из текста на естественном языке.

    :param raw_response: Исходный ответ LLM-агента.
    :type raw_response: str
    :return: Разобранный список 'тезисных' триплетов из ответа LLM-агента.
    :rtype: Tuple[List[Tuple[str, str]], ReturnStatus]
    """
    status = ReturnStatus.success
    if ":" in raw_response:
        raw_response = raw_response.split(":")[-1]
    raw_response = raw_response.lower()
    raw_response = raw_response.split(".")
    raw_triplets = []
    for raw_thesis in raw_response:
        if ";" not in raw_thesis:
            continue
        try:
            raw_thesis, raw_entities = raw_thesis.split(";")
            thesis = raw_thesis.strip('.-* ')
            entities = ast.literal_eval(raw_entities.strip(''' \n'".,/'''))
        except:
            continue
        raw_triplets.append((thesis, entities))

    if len(raw_triplets) == 0:
        status = ReturnStatus.bad_format

    return raw_triplets, status

def ethesises_custom_formate():
    # TODO
    pass

def ethesises_custom_postprocess(self, parsed_answer: object, node_prop: Dict, rel_prop: Dict) -> Tuple[List[Triplet], ReturnStatus]:
    formated_triplets = []
    for triplet in raw_triplets:
        thesis, entities = triplet

        thesis_node = NodeCreator.create(name=str(thesis), n_type=NodeType.hyper, prop={**node_prop})
        thesis_rel = Relation(name=RelationType.hyper.value, type=RelationType.hyper, prop={**rel_prop})
        for entity in entities:
            formated_triplets.append(TripletCreator.create(
                NodeCreator.create(name=str(entity), n_type=NodeType.object, prop={**node_prop}),
                thesis_rel, thesis_node))

    return formated_triplets, status
