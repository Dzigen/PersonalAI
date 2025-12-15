import re

from typing import List, Dict, Any, Tuple

def rephrase_chunk_custom_formate(chunk_messages: List[Dict[str, Any]]) -> str:
    msgs_list = []
    for i, msg in enumerate(chunk_messages):
        speaker = msg.get("speaker", "")
        msg_text = msg.get("processed_text") or msg.get("text") or ""
        msg_text = re.sub(r'\n{3,}', '\n\n', msg_text)
        text = f'{i + 1}. ||{speaker}||: "{msg_text}"'
        msgs_list.append(text)

    dialogue = '\n\n\n'.join(msgs_list)

    if len(dialogue) < 1:
        raise ValueError

    return {'dialogue': dialogue}


def rephrase_chunk_custom_postprocess(parsed_response_tuple: Tuple[List[str], str], **kwargs) -> Tuple[List[str], str]:
    parsed_response, raw_response = parsed_response_tuple
    if len(parsed_response) < 1:
        raise ValueError(f"parsed_response: '{parsed_response}'")

    clear_parsed_response = []
    for raw_msg in parsed_response:
        msg = raw_msg.split('||')[-1].strip().strip('"')
        msg = msg.strip().strip(':').strip().strip('"')
        clear_parsed_response.append(msg)
    return list(map(lambda subq: subq.strip(), clear_parsed_response)), raw_response
