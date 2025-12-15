def quest_reph_custom_answer_parse(raw_response: str, **kwargs) -> str:
    prefix = "[Rephrased question]"
    prefixed_answer = raw_response.strip()
    answer = None
    if prefixed_answer.startswith(prefix):
        answer = prefixed_answer[len(prefix):].strip()
    else:
        answer = prefixed_answer

    filtered_response = answer.strip("\n\t ")
    if len(filtered_response) < 1:
        raise ValueError(f"raw_response: '{raw_response}'")

    return filtered_response
