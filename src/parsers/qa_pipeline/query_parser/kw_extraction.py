from typing import List, Dict


def kwe_custom_formate(query: str) -> Dict[str, str]:
    if len(query) < 1:
        raise ValueError

    return {'text': query}

def kwe_custom_parse(raw_response: str, **kwargs) -> List[str]:
    """Функция предназначена для разбора ответа от LLM-агента, в рамках задачи по извлечению ключевых сущностей из текста на естественном языке.

    :param raw_response: Исходный ответ LLM-агента.
    :type raw_response: str
    :return: Разобранный список ключевых сущностей из ответа LLM-агента.
    :rtype: List[str]
    """

    # Пустой ответ
    if len(raw_response) < 1:
        raise ValueError

    extracted_entities = list(map(lambda item: item.strip(), raw_response.split('|')))

    # Ошибка в формате ответа
    for entitie in extracted_entities:
        if len(entitie) < 1:
            raise ValueError

    return extracted_entities

def kwe_custom_postprocess(parsed_response: List[str], **kwargs) -> List[str]:
    if len(parsed_response) < 1:
        raise ValueError

    return parsed_response
