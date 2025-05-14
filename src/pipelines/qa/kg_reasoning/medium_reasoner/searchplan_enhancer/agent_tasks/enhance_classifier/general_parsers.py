from typing import List, Dict

def enhcls_custom_formate(query: str, search_steps: List[str], steps_answers: List[str]) -> Dict[str, str]:
    if len(query) < 1 or len(search_steps) < 1 or len(steps_answers) != len(search_steps):
        raise ValueError
    
    # TODO
    
    return ...

def enhcls_custom_postprocess(parsed_response: str, **kwargs) -> bool:
    if len(parsed_response) < 1:
        raise ValueError
    
    need_decompose = None
    if parsed_response == '<|enhanc|>':
        need_decompose = True
    elif parsed_response == '<|noneed|>':
        need_decompose = False
    else:
        raise ValueError

    return need_decompose