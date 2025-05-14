from typing import List, Dict

from ....utils import SearchPlanInfo

def answcls_custom_formate(search_plan: SearchPlanInfo) -> Dict[str, str]:

    # TODO
    
    return ...

def answcls_custom_postprocess(parsed_response: str, **kwargs) -> bool:
    if len(parsed_response) < 1:
        raise ValueError
    
    can_answer = None
    if parsed_response == '<|can|>':
        can_answer = True
    elif parsed_response == '<|not|>':
        can_answer = False
    else:
        raise ValueError

    return can_answer