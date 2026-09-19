from typing import List
import re


def cagen_custom_parse(raw_response: str, **kwargs) -> List[str]:
    if len(raw_response) < 1:
        raise ValueError(f"raw_response: '{raw_response}'")

    prefix = "[Relevant Summary]"
    prefixed_answer = raw_response.strip()
    answer = None
    if prefixed_answer.startswith(prefix):
        answer = prefixed_answer[len(prefix):].strip()
    else:
        answer = prefixed_answer

    # Пустой ответ
    if len(answer) < 1:
        raise ValueError(f"raw_response: '{raw_response}'")

    return answer
