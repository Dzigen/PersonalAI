from typing import List

def qgen_custom_parse(raw_response: str, **kwargs) -> List[str]:
    if len(raw_response) < 1:
        raise ValueError

    cluequery = None
    # TODO    

    return cluequery