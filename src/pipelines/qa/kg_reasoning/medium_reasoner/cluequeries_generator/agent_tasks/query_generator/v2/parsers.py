from typing import List


def cqgen_custom_parse(raw_response: str, **kwargs) -> List[str]:
    if len(raw_response) < 1:
        raise ValueError(f"raw_response: '{raw_response}'")

    cluequery = raw_response.strip()

    return cluequery
