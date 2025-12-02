from typing import List


def cqgen_custom_parse(raw_response: str, **kwargs) -> List[str]:
    if len(raw_response) < 1:
        raise ValueError(f"raw_response: '{raw_response}'")

    prefix = "[Specific question]"
    prefixed_cluequery = raw_response.strip()
    cluequery = None
    if prefixed_cluequery.startswith(prefix):
        cluequery = prefixed_cluequery[len(prefix):].strip()
    else:
        cluequery = prefixed_cluequery

    # Пустой ответ
    if len(cluequery) < 1:
        raise ValueError(f"raw_response: '{raw_response}'")

    return cluequery
