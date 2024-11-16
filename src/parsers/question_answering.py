from typing import Tuple

from ..utils import ReturnStatus

def qa_custom_answer_parse_func_en(raw_response: str) -> Tuple[str, ReturnStatus]:
    """Функция предназначена для разбора результата генерации ответа LLM-агента, в рамаках условной QA-задачи на английском языке.

    :param raw_response: Исходный ответ LLM-агента.
    :type raw_response: str
    :return: Разобранный ответ на user-вопрос от LLM-агента.
    :rtype: Tuple[str, ReturnStatus]
    """
    status = ReturnStatus.success
    found_line = ""
    for line in raw_response.split("\n"):
        if "Final answer 3" in line:
            found_line = line
            break
    if found_line:
        answer = found_line.split("Final answer 3: ")[-1]
    else:
        answer = raw_response
    return answer, status

def qa_custom_answer_parse_func_ru(raw_response: str) -> Tuple[str, ReturnStatus]:
    """Функция предназначена для разбора результата генерации ответа LLM-агента, в рамаках условной QA-задачи на русском языке.

    :param raw_response: Исходный ответ LLM-агента.
    :type raw_response: str
    :return: Разобранный ответ на user-вопрос от LLM-агента.
    :rtype: Tuple[str, ReturnStatus]
    """
    status = ReturnStatus.success
    return raw_response, status
