from typing import List, Dict, Set

from ......utils import Triplet
from ......utils.data_structs import create_id


def rs_custom_formate(base_triplet: Triplet, incident_triplets: List[Triplet]) -> Dict[str, str]:
    """Функция формирует словарь контекста для LLM-задачи по замене simple-триплетов.

    :param base_triplet: Базовый simple-триплет, относительно которого определяется устаревшая информация.
    :type base_triplet: Triplet
    :param incident_triplets: Список триплетов, инцидентных базовому триплету и рассматриваемых как кандидаты на устаревание.
    :type incident_triplets: List[Triplet]
    :return: Словарь с контекстом, передаваемый в LLM-подзадачу.
    :rtype: Dict[str, str]
    """
    if len(incident_triplets) < 1:
        raise ValueError

    def _custom_triplet_stringify(triplet: Triplet) -> str:
        return f"{triplet.start_node.name}, {triplet.relation.name}, {triplet.end_node.name}"

    new_str_triplet = f'"{_custom_triplet_stringify(base_triplet)}"'
    existing_str_triplets = '; '.join(
        map(lambda triplet: f'"{_custom_triplet_stringify(triplet)}"', incident_triplets))

    return {'ex_triplets': existing_str_triplets, 'new_triplets': new_str_triplet}


def rs_custom_postprocess(parsed_response: Dict[str, Set[str]], base_triplet: Triplet, incident_triplets: List[Triplet]) -> List[str]:
    """Функция предназначена для постобработки ответа LLM-агента в задаче замены simple-триплетов.

    :param parsed_response: Результат парсинга ответа LLM-агента: соответствие идентификаторов новых триплетов и множеств идентификаторов устаревших триплетов.
    :type parsed_response: Dict[str, Set[str]]
    :param base_triplet: Базовый триплет, относительно которого строился контекст.
    :type base_triplet: Triplet
    :param incident_triplets: Список триплетов-кандидатов на устаревание.
    :type incident_triplets: List[Triplet]
    :return: Список идентификаторов триплетов, подлежащих удалению из графа знаний.
    :rtype: List[str]
    """
    if len(incident_triplets) < 1:
        raise ValueError(f"parsed_response: '{parsed_response}'")

    def _custom_triplet_stringify(triplet: Triplet) -> str:
        return f"{triplet.start_node.name}, {triplet.relation.name}, {triplet.end_node.name}"

    custom_ids_to_triplets = {create_id(_custom_triplet_stringify(
        triplet)): triplet for triplet in incident_triplets}
    base_triplet_custom_id = create_id(_custom_triplet_stringify(base_triplet))
    obsolete_str_ids = parsed_response.get(base_triplet_custom_id, [])

    triplet_ids_to_remove = []
    for custom_id in custom_ids_to_triplets.keys():
        if custom_id in obsolete_str_ids:
            triplet_ids_to_remove.append(custom_ids_to_triplets[custom_id].id)

    return triplet_ids_to_remove
