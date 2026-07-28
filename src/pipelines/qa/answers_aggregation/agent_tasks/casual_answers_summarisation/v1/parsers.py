import re


def csubasumm_custom_answer_parse(raw_response: str, **kwargs) -> str:

    if len(raw_response) < 1:
        raise ValueError(f"raw_response (init): '{raw_response}'")

    answer_pos = re.search(r"\[answer\]", raw_response, re.IGNORECASE)

    # Ответ не соответствует формату
    if answer_pos is None:
        raise ValueError(f"raw_response (format error): '{raw_response}'")

    answer = raw_response[answer_pos.span(0)[1]:].strip()

    # Пустой ответ
    if len(answer) < 1:
        raise ValueError(f"raw_response (after filtering): '{raw_response}'")

    return answer
