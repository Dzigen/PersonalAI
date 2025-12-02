from typing import List, Dict, Set

from ......utils import Triplet
from ......utils.data_structs import create_id


def rt_custom_formate(base_triplet: Triplet, incident_triplets: List[Triplet]) -> Dict[str, str]:
    """Функция формирует словарь контекста для LLM-задачи по замене тезисных (hyper-) триплетов.

    :param base_triplet: Базовый триплет, относительно которого определяется устаревшая информация.
    :type base_triplet: Triplet
    :param incident_triplets: Список триплетов, инцидентных базовому триплету и рассматриваемых как кандидаты на устаревание.
    :type incident_triplets: List[Triplet]
    :return: Словарь с контекстом, передаваемый в LLM-подзадачу.
    :rtype: Dict[str, str]
    """
    if len(incident_triplets) < 1:
        raise ValueError

    def _custom_thesis_stringify(triplet: Triplet) -> str:
        return triplet.end_node.name

    new_str_thesise = f'["{_custom_thesis_stringify(base_triplet)}"]'
    existing_str_thesises = '[' + ', '.join(map(
        lambda triplet: f'"{_custom_thesis_stringify(triplet)}"', incident_triplets)) + ']'

    return {'ex_thesises': existing_str_thesises, 'new_thesises': new_str_thesise}


def rt_custom_postprocess(parsed_response: Dict[str, Set[str]], base_triplet: Triplet, incident_triplets: List[Triplet]) -> List[str]:
    """Функция предназначена для постобработки ответа LLM-агента в задаче замены тезисных (hyper-) триплетов.

    :param parsed_response: Результат парсинга ответа LLM-агента: соответствие идентификаторов новых тезисов и множеств идентификаторов устаревших тезисов.
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

    def _custom_thesis_stringify(triplet: Triplet) -> str:
        return triplet.end_node.name

    custom_ids_to_triplets = {create_id(_custom_thesis_stringify(
        triplet)): triplet for triplet in incident_triplets}
    base_triplet_custom_id = create_id(_custom_thesis_stringify(base_triplet))
    obsolete_str_ids = parsed_response.get(base_triplet_custom_id, [])

    triplet_ids_to_remove = []
    for custom_id in custom_ids_to_triplets.keys():
        if custom_id in obsolete_str_ids:
            triplet_ids_to_remove.append(custom_ids_to_triplets[custom_id].id)

    return triplet_ids_to_remove
