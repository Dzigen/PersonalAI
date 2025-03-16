from typing import Dict, List

def llmjudge_custom_formate(gold_answer: str, generated_answer: str) -> Dict[str, str]:
    if len(generated_answer) < 1:
        raise ValueError

    return {'gold_answer': gold_answer, 'gen_answer': generated_answer}

def llmjudge_custom_postprocess(parsed_response: str, **kwargs) -> int:
    if len(parsed_response) < 1:
        raise ValueError

    judge_score = int(parsed_response)
    return judge_score
