from typing import List

def answ_rephrase_custom_formate(question: str, rephrased_question: str, raw_answer: str) -> str:
    if len(question) < 1:
        raise ValueError

    return {'question': question, 'rephrased_question': rephrased_question, 'raw_answer': raw_answer}


def answ_rephrase_custom_postprocess(parsed_response:str, **kwargs) -> str:
    if len(parsed_response) < 1:
        raise ValueError(f"parsed_response: '{parsed_response}'")

    return parsed_response
