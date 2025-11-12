from typing import List
import re


def cagen_custom_parse(raw_response: str, **kwargs) -> List[str]:
    if len(raw_response) < 1:
        raise ValueError(f"raw_response: '{raw_response}'")

    answer = raw_response.strip()

    # Пустой ответ
    if len(answer) < 1:
        raise ValueError(f"raw_response: '{raw_response}'")

    return answer
