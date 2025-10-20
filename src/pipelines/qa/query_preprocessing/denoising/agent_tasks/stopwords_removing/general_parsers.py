from typing import List


def swremv_custom_formate(query: str) -> str:
    if len(query) < 1:
        raise ValueError

    return {'query': query}


def swremv_custom_postprocess(parsed_response: str, **kwargs) -> str:
    if len(parsed_response) < 1:
        raise ValueError(f"parsed_response: '{parsed_response}'")

    return parsed_response
