from typing import List
import re


def canswgen_custom_parse(raw_response: str, **kwargs) -> List[str]:
    if len(raw_response) < 1:
        raise ValueError(f"raw_response (init): '{raw_response}'")

    # Ответ не соответствует формату
    answer_pos = re.search(r"\[answer\]", raw_response, re.IGNORECASE)
    if answer_pos is None:
        raise ValueError(f"raw_response (format error): '{raw_response}'")
    answer = raw_response[answer_pos.span(0)[1]:].strip()

    # костыль #1: иногда в ответе дополнииельно генерируется '[Final Answer]'-директива
    final_answer_pos = re.search(r"\[final answer\]", answer, re.IGNORECASE)
    if final_answer_pos is not None:
        answer = answer[final_answer_pos.span(0)[1]:].strip()

    # костыль #2: иногда в ответе дополнииельно генерируется 'Финальный ответ:'-директива
    final_answer_pos = re.search(r"финальный ответ:", answer, re.IGNORECASE)
    if final_answer_pos is not None:
        answer = answer[final_answer_pos.span(0)[1]:].strip()

    # костыль #3: иногда в ответе дополнииельно генерируется 'окончательный ответ:'-директива
    final_answer_pos = re.search(r"окончательный ответ:", answer, re.IGNORECASE)
    if final_answer_pos is not None:
        answer = answer[final_answer_pos.span(0)[1]:].strip()

    # Пустой ответ
    if len(answer) < 1:
        raise ValueError(f"raw_response (after filtering): '{raw_response}'")

    return answer
