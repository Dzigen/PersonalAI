from typing import List

def dc_custom_formate(query: str) -> str:
    if len(query) < 1:
        raise ValueError

    return {'query': query}

def dc_custom_postprocess(parsed_response: str, **kwargs) -> bool:
    if len(parsed_response) < 1:
        raise ValueError
    
    need_decompose = None
    if parsed_response == '<|decomp|>':
        need_decompose = True
    elif parsed_response == '<|noneed|>':
        need_decompose = False
    else:
        raise ValueError

    return need_decompose