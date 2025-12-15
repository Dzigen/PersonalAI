from typing import List

def fct_preserv_custom_formate(text: str, prev_context: str, next_context: str) -> str:
    if len(text) < 1:
        raise ValueError

    return {'prev_context': prev_context, 'text': text, 'next_context': next_context}


def fct_preserv_custom_postprocess(parsed_response:str, **kwargs) -> str:
    if len(parsed_response) < 1:
        raise ValueError(f"parsed_response: '{parsed_response}'")

    return parsed_response
