from typing import List

def quest_rephrase_custom_formate(question: str) -> str:
    if len(question) < 1:
        raise ValueError

    return {'question': question}


def quest_rephrase_custom_postprocess(parsed_response:str, **kwargs) -> str:
    if len(parsed_response) < 1:
        raise ValueError(f"parsed_response: '{parsed_response}'")

    return parsed_response
