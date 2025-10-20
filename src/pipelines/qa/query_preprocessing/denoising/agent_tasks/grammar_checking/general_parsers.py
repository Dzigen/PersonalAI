from typing import List


def gramcheck_custom_formate(query: str) -> str:
    if len(query) < 1:
        raise ValueError

    return {'query': query}


def gramcheck_custom_postprocess(parsed_response: List[str], **kwargs) -> str:
    if len(parsed_response) < 1:
        raise ValueError(f"parsed_response: '{parsed_response}'")

    return parsed_response
