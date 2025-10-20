from typing import List
import re


def dc_custom_formate(query: str) -> str:
    if len(query) < 1:
        raise ValueError

    return {'query': query}


def dc_custom_postprocess(parsed_response: str, **kwargs) -> bool:
    if len(parsed_response) < 1:
        raise ValueError(f"parsed_response: '{parsed_response}'")

    true_matches = re.findall(r"[^\w]*True[^\w]*", parsed_response)
    false_matches = re.findall(r"[^\w]*False[^\w]*", parsed_response)

    if len(true_matches) > 0:
        candecomp_sign = True
    elif len(false_matches) > 0:
        candecomp_sign = False
    else:
        raise ValueError(f"parsed_response: '{parsed_response}'")

    return candecomp_sign
