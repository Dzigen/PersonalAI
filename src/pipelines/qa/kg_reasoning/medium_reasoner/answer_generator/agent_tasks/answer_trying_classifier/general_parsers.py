from typing import List, Dict
import re

from ........utils.data_structs import SearchPlanInfo


def answcls_custom_formate(search_plan: SearchPlanInfo) -> Dict[str, str]:
    search_info = '\n\n'.join(list(map(
        lambda i: f'[Search Query #{i}]\n{search_plan.search_steps[i]}\n[Finded Information]\n{search_plan.steps_answers[i]}', range(len(search_plan.steps_answers)))))

    return {'query': search_plan.base_query, 'search_info': search_info}


def answcls_custom_postprocess(parsed_response: str, **kwargs) -> bool:
    if len(parsed_response) < 1:
        raise ValueError(f"parsed_response: '{parsed_response}'")

    true_matches = re.findall(r"[^\w]*True[^\w]*", parsed_response)
    false_matches = re.findall(r"[^\w]*False[^\w]*", parsed_response)

    if len(true_matches) > 0:
        cananswer_sign = True
    elif len(false_matches) > 0:
        cananswer_sign = False
    else:
        raise ValueError(f"parsed_response: '{parsed_response}'")

    return cananswer_sign
