from src.utils import AgentTaskSuite

from .parsers import reph_chunk_custom_answer_parse
from .prompts import \
    EN_REPH_CHUNK_SYSTEM_PROMPT, EN_REPH_CHUNK_USER_PROMPT, EN_REPH_CHUNK_ASSISTANT_PROMPT, \
    RU_REPH_CHUNK_SYSTEM_PROMPT, RU_REPH_CHUNK_USER_PROMPT, RU_REPH_CHUNK_ASSISTANT_PROMPT


EN_REPH_CHUNK_SUITE = AgentTaskSuite(
    system_prompt=EN_REPH_CHUNK_SYSTEM_PROMPT,
    user_prompt=EN_REPH_CHUNK_USER_PROMPT,
    assistant_prompt=EN_REPH_CHUNK_ASSISTANT_PROMPT,
    parse_answer_func=reph_chunk_custom_answer_parse
)

RU_REPH_CHUNK_SUITE = AgentTaskSuite(
    system_prompt=RU_REPH_CHUNK_SYSTEM_PROMPT,
    user_prompt=RU_REPH_CHUNK_USER_PROMPT,
    assistant_prompt=RU_REPH_CHUNK_ASSISTANT_PROMPT,
    parse_answer_func=reph_chunk_custom_answer_parse
)

REPH_CHUNK_SUITE_V1 = {
    'ru': RU_REPH_CHUNK_SUITE, 'en': EN_REPH_CHUNK_SUITE}
