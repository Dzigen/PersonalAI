from typing import List

def subasumm_custom_formate(query: str, sub_queries: List[str], sub_answers: List[str]) -> str:
    if len(query) < 1 or len(sub_queries) < 2 or len(sub_answers) != len(sub_queries):
        raise ValueError
    
    # TODO

    return {'query': query}

def subasumm_custom_postprocess(parsed_response: List[str], **kwargs) -> List[str]:
    if len(parsed_response) < 1:
        raise ValueError

    return parsed_response