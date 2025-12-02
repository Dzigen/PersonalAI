from typing import List
import re


def summn_custom_parse(raw_response: str, **kwargs) -> str:
    """Метод предназначен для парсинга сырого ответа LLM и извлечения текстового резюме.

    Ожидается, что резюме следует за [Output Summary]. Если шаблон не найден, возвращается весь исходный ответ.

    :param raw_response: Сырой текстовый ответ LLM.
    :type raw_response: str
    :return: Строка с итоговым резюме.
    :rtype: str
    """
    # Пустой ответ
    raw_response = raw_response.strip(' .')
    if len(raw_response) < 1:
        raise ValueError(f"raw_response: '{raw_response}'")

    summary = None
    finded_pattern = re.search(r"\[Output Summary\]\n(.+?)$", raw_response)
    if finded_pattern is not None:
        summary = finded_pattern.group(1)
    else:
        summary = raw_response

    return summary
