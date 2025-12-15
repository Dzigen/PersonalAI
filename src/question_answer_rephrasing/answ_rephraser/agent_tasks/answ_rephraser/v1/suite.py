from src.utils import AgentTaskSuite

from .parsers import answ_reph_custom_answer_parse
from .prompts import \
    EN_ANSW_REPH_SYSTEM_PROMPT, EN_ANSW_REPH_USER_PROMPT, EN_ANSW_REPH_ASSISTANT_PROMPT, \
    RU_ANSW_REPH_SYSTEM_PROMPT, RU_ANSW_REPH_USER_PROMPT, RU_ANSW_REPH_ASSISTANT_PROMPT


EN_ANSW_REPH_SUITE = AgentTaskSuite(
    system_prompt=EN_ANSW_REPH_SYSTEM_PROMPT,
    user_prompt=EN_ANSW_REPH_USER_PROMPT,
    assistant_prompt=EN_ANSW_REPH_ASSISTANT_PROMPT,
    parse_answer_func=answ_reph_custom_answer_parse
)

RU_ANSW_REPH_SUITE = AgentTaskSuite(
    system_prompt=RU_ANSW_REPH_SYSTEM_PROMPT,
    user_prompt=RU_ANSW_REPH_USER_PROMPT,
    assistant_prompt=RU_ANSW_REPH_ASSISTANT_PROMPT,
    parse_answer_func=answ_reph_custom_answer_parse
)

ANSW_REPH_SUITE_V1 = {
    'ru': RU_ANSW_REPH_SUITE, 'en': EN_ANSW_REPH_SUITE}
