from typing import List, Tuple
import re


def reph_chunk_custom_answer_parse(raw_response: str, **kwargs) -> Tuple[List[str], str]:
    if len(raw_response) < 1:
        raise ValueError(f"raw_response: '{raw_response}'")

    prefix = "[Rephrased dialogue]"
    prefixed_answer = raw_response.strip()
    answer = None
    if prefixed_answer.startswith(prefix):
        answer = prefixed_answer[len(prefix):].strip()
    else:
        answer = prefixed_answer

    if len(answer) < 1:
        raise ValueError(f"raw_response: '{raw_response}'")

    answer = re.sub(r'\n\s*\n\s*\n', '\n\n\n', answer)
    parsed_subq = list(
        filter(lambda sub_q: len(sub_q), answer.split("\n\n\n")))

    formated_subq = list(filter(lambda sub_q: len(sub_q), parsed_subq))
    if len(formated_subq) < 1:
        raise ValueError(f"raw_response: '{formated_subq}'")

    return formated_subq, answer
