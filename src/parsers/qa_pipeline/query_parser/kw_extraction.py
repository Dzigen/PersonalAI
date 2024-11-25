from typing import List, Dict


def kwe_custom_formate(query: str) -> Dict[str, str]:
    return {'text': query}

def kwe_custom_parse(raw_response: str) -> List[str]:
    """Функция предназначена для разбора ответа от LLM-агента, в рамаках задачи по извлечению ключевых сущностей из текста на естественном языке.

    :param raw_response: Исходный ответ LLM-агента.
    :type raw_response: str
    :return: Разобранный список ключевых сущностей из ответа LLM-агента.
    :rtype: List[str]
    """
    entities = list(filter(lambda item: len(item) > 0, list(map(lambda item: item.strip(), raw_response.split('|')))))
    return entities

def kwe_custom_postprocess(parsed_response: List[str]) -> List[str]:
    return parsed_response
