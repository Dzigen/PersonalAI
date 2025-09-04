from typing import List

def swremv_custom_parse(raw_response: str, **kwargs) -> str:
    filtered_response = raw_response.strip("\n\t ")
    if len(filtered_response) < 1:
        raise ValueError

    return filtered_response
