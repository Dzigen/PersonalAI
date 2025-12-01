from typing import List


def lcheck_custom_formate(query: str) -> str:
    """Функция готовит контекст для промпта задачи исправления ошибок в запросе.

    :param query: Исходный текст запроса.
    :type query: str
    :return: Словарь с полем 'query', передаваемый в LLM-подзадачу.
    :rtype: Dict[str, str]
    """
    if len(query) < 1:
        raise ValueError

    return {'query': query}


def lcheck_custom_postprocess(parsed_response: List[str], **kwargs) -> str:
    """Функция предназначена для постобработки разобранного ответа LLM-агента в задаче исправления ошибок в запросе.

    :param parsed_response: Результат парсера ответа LLM-агента (список строк).
    :type parsed_response: List[str]
    :return: Исходный parsed_response, если он непустой.
    :rtype: List[str]
    """
    if len(parsed_response) < 1:
        raise ValueError(f"parsed_response: '{parsed_response}'")

    return parsed_response
