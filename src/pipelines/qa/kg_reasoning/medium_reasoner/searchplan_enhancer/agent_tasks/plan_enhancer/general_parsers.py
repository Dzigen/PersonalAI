from typing import List, Dict

def planenh_custom_formate(query: str, passed_steps: List[str], steps_answers: List[str]) -> Dict[str, str]:
    if len(query) < 1 or len(passed_steps) < 1 or len(steps_answers) != len(passed_steps):
        raise ValueError
    
    return {'query': query, 'passed_steps': passed_steps, 'steps_answers': steps_answers}

def planenh_custom_postprocess(parsed_response: List[str], **kwargs) -> List[str]:
    if len(parsed_response) < 1:
        raise ValueError

    return parsed_response