from typing import List
import re


def dc_custom_formate(query: str) -> str:
    """Функция готовит контекст для промпта задачи классификации на предмет необходимости декомпозиции запроса.

    :param query: Исходный текст запроса.
    :type query: str
    :return: Словарь с полем 'query', передаваемый в LLM-подзадачу.
    :rtype: Dict[str, str]
    """
    if len(query) < 1:
        raise ValueError

    return {'query': query}


def dc_custom_postprocess(parsed_response: str, **kwargs) -> bool:
    """Функция предназначена для постобработки ответа LLM-агента в задаче классификации на предмет необходимости декомпозиции запроса.

    В тексте ответа ищутся вхождения ключевых слов True и False.
    На основе найденных вхождений определяется булев признак, показывающий, нужно ли разбивать исходный вопрос на под-вопросы.

    :param parsed_response: Строка с ответом LLM-агента, содержащая пометку True или False.
    :type parsed_response: str
    :return: Булев признак необходимости декомпозиции (True — требуется декомпозиция, False — декомпозиция не требуется).
    :rtype: bool
    """
    if len(parsed_response) < 1:
        raise ValueError(f"parsed_response: '{parsed_response}'")

    true_matches = re.findall(r"[^\w]*True[^\w]*", parsed_response)
    false_matches = re.findall(r"[^\w]*False[^\w]*", parsed_response)

    if len(true_matches) > 0:
        candecomp_sign = True
    elif len(false_matches) > 0:
        candecomp_sign = False
    else:
        raise ValueError(f"parsed_response: '{parsed_response}'")

    return candecomp_sign
