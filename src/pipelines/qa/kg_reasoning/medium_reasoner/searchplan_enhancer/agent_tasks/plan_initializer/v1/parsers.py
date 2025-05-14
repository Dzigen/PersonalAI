from typing import List

def planinit_custom_parse(raw_response: str, **kwargs) -> List[str]:
    if len(raw_response) < 1:
        raise ValueError

    search_steps = None
    # TODO    

    return search_steps