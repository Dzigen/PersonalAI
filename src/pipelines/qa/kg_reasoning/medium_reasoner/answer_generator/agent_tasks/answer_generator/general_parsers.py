from typing import List, Dict

from ....utils import SearchPlanInfo

def answgen_custom_formate(search_plan: SearchPlanInfo) -> Dict[str, str]:

    # TODO
    
    return ...

def answgen_custom_postprocess(parsed_response: str, **kwargs) -> bool:
    if len(parsed_response) < 1:
        raise ValueError

    return parsed_response