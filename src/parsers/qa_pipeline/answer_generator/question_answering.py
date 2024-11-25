from typing import Tuple, List

from ....utils import ReturnStatus, Triplet, TripletCreator

def en_ag_custom_answer_parse(raw_response: str) -> Tuple[str, ReturnStatus]:
    """Функция предназначена для разбора результата генерации ответа LLM-агента, в рамаках условной QA-задачи на английском языке.

    :param raw_response: Исходный ответ LLM-агента.
    :type raw_response: str
    :return: Разобранный ответ на user-вопрос от LLM-агента.
    :rtype: Tuple[str, ReturnStatus]
    """
    status = ReturnStatus.success
    found_line = ""
    for line in raw_response.strip().split("\n"):
        if "Final answer 3" in line:
            found_line = line
            break
    if found_line:
        answer = found_line.split("Final answer 3: ")[-1]
    else:
        answer = raw_response
    return answer, status

def ru_ag_custom_answer_parse(raw_response: str) -> Tuple[str, ReturnStatus]:
    """Функция предназначена для разбора результата генерации ответа LLM-агента, в рамаках условной QA-задачи на русском языке.

    :param raw_response: Исходный ответ LLM-агента.
    :type raw_response: str
    :return: Разобранный ответ на user-вопрос от LLM-агента.
    :rtype: Tuple[str, ReturnStatus]
    """
    status = ReturnStatus.success
    raw_response = raw_response.strip()
    return raw_response, status

def ag_custom_foramte(query: str, triplets: List[Triplet]) -> str:
    """Метод предназначен для предтсавления набора триплетов
    в виде ненумерованного списка с их строковыми представлениями на естественном языке.

    :param triplets: Набор триплетов.
    :type triplets: List[Triplet]
    :return: Ненумепованный список со строковыми представлениями триплетов.
    :rtype: str
    """
    filtered_context = list(map(lambda triplet: f"- {(TripletCreator.stringify(triplet)[1] if triplet.stringified is None else triplet.stringified).strip()}", triplets))
    return {'c':"\n".join(filtered_context), 'q': query}

def ag_custom_postprocess(parsed_response: object) -> str:
    return parsed_response
