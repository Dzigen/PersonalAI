from typing import List, Tuple, Dict

from ....utils import ReturnStatus


def kwe_custom_formate() -> Dict[str, str]:
    # TODO
    pass

def kwe_custom_parse(raw_response: str) -> List[str]:
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

def kwe_custom_postprocess(parsed_response: Dict[str, object]):
    # TODO
    pass
