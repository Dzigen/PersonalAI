from typing import Dict
from collections import defaultdict

from .......utils.data_structs import create_id


def rt_custom_parse(raw_response: str, **kwargs) -> Dict[str, object]:
    """Функция парсит сырой ответ LLM-агента в задаче замены тезисных (hyper-) триплетов.

    :param raw_response: Сырой ответ LLM-агента.
    :type raw_response: str
    :return: Словарь, в котором ключами являются идентификаторы новых тезисов, а значениями — множества идентификаторов тезисов, которые считаются устаревшими.
    :rtype: Dict[str, object]
    """
    if len(raw_response) < 1:
        raise ValueError(f"raw_response: '{raw_response}'")

    raw_replacements = raw_response.lower()
    predicted_outdated = raw_replacements.split(
        "[")[-1].split("]")[0].split('", "')
    thesises_to_remove = defaultdict(set)
    for pair in predicted_outdated:
        splitted_pair = pair.split("<-")
        if len(splitted_pair) != 2:
            continue

        str_existing_thesis = splitted_pair[1].strip(''' \n'".,/''')
        str_new_thesis = splitted_pair[0].strip(''' \n'".,/''')
        thesises_to_remove[create_id(str_new_thesis)].add(
            create_id(str_existing_thesis))

    return thesises_to_remove
