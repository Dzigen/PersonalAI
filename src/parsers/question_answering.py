

def qa_custom_answer_parse_func_en(raw_response: str):
    found_line = ""
    for line in raw_response.split("\n"):
        if "Final answer 3" in line:
            found_line = line
            break
    if found_line:
        answer = found_line.split("Final answer 3: ")[-1]
    else:
        answer = raw_response
    return answer

def qa_custom_answer_parse_func_ru(raw_response: str) -> str:
    return raw_response
