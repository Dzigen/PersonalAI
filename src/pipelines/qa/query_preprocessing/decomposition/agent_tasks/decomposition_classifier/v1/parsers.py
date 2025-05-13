from typing import List
import re

def dc_custom_answer_parse(raw_response: str, **kwargs) -> List[str]:
    if len(raw_response) < 1:
        raise ValueError
    
    sign = re.search("\<\|[\w]{6}\|\>", raw_response)
    if sign is None:
        raise ValueError
    sign = sign.group(0)

    return sign