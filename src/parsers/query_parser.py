from typing import List

def qa_custom_entities_parse_func(raw_response: str) -> List[str]:
    return list(filter(lambda item: len(item) > 0, list(map(lambda item: item.strip(), raw_response.split('|')))))
