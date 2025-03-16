from typing import List

def llmjudge_custom_parse(raw_response: str, **kwargs) -> List[str]:
    if len(raw_response) < 1:
        raise ValueError

    cleaned_response = raw_response.strip()
    return cleaned_response[0]
