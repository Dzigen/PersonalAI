from typing import List
import re


def au_clf_custom_answer_parse(raw_response: str, **kwargs) -> List[str]:
    if len(raw_response) < 1:
        raise ValueError(f"raw_response: '{raw_response}'")

    answer_pos = re.search(r"\[answer\]", raw_response, re.IGNORECASE)

    # Ответ не соответствует формату
    if answer_pos is None:
        raise ValueError(f"raw_response: '{raw_response}'")

    answer = raw_response[answer_pos.span(0)[1]:].strip()

    # Пустой ответ
    if len(answer) < 1:
        raise ValueError(f"raw_response: '{raw_response}'")

    return answer