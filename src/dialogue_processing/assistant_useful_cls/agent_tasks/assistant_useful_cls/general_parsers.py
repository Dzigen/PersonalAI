import re

from typing import List

def assist_use_cls_custom_formate( assistant_text: str, prev_user_text: str, next_user_text: str) -> str:
    if len(assistant_text) < 1:
        raise ValueError

    return {'assistant_text': assistant_text, 'prev_user_text': prev_user_text, 'next_user_text': next_user_text}


def assist_use_cls_custom_postprocess(parsed_response:str, **kwargs) -> str:
    if len(parsed_response) < 1:
        raise ValueError(f"parsed_response: '{parsed_response}'")

    true_matches = re.findall(r"[^\w]*True[^\w]*", parsed_response)
    false_matches = re.findall(r"[^\w]*False[^\w]*", parsed_response)

    if len(true_matches) > 0:
        assist_use_sign = True
    elif len(false_matches) > 0:
        assist_use_sign = False
    else:
        raise ValueError(f"parsed_response: '{parsed_response}'")

    return assist_use_sign
