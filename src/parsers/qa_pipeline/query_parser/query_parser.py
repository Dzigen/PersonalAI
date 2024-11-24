from typing import List, Tuple

from ..utils import ReturnStatus

def qa_custom_entities_parse_func(raw_response: str) -> Tuple[List[str], ReturnStatus]:
    """Функция предназначена для разбора результата генерации ответа LLM-агента, в рамаках задачи по извлечению ключевых сущностей из текста на естественном языке.

    :param raw_response: Исходный ответ LLM-агента.
    :type raw_response: str
    :return: Разобранный список ключевых сущностей из ответа LLM-агента.
    :rtype: Tuple[List[str], ReturnStatus]
    """
    status = ReturnStatus.success
    entities = list(filter(lambda item: len(item) > 0, list(map(lambda item: item.strip(), raw_response.split('|')))))
    if len(entities) == 0:
        status = ReturnStatus.bad_format
    return entities, status
