from .........utils import AgentTaskSuite

from .parsers import searchscls_custom_parse

from .prompts import EN_SEARCHSCLS_SYSTEM_PROMPT, EN_SEARCHSCLS_USER_PROMPT, EN_SEARCHSCLS_ASSISTANT_PROMPT, \
    RU_SEARCHSCLS_SYSTEM_PROMPT, RU_SEARCHSCLS_USER_PROMPT, RU_SEARCHSCLS_ASSISTANT_PROMPT

EN_SEARCHSCLS_SUITE = AgentTaskSuite(
    system_prompt=EN_SEARCHSCLS_SYSTEM_PROMPT,
    user_prompt=EN_SEARCHSCLS_USER_PROMPT,
    assistant_prompt=EN_SEARCHSCLS_ASSISTANT_PROMPT,
    parse_answer_func=searchscls_custom_parse
)

RU_SEARCHSCLS_SUITE = AgentTaskSuite(
    system_prompt=RU_SEARCHSCLS_SYSTEM_PROMPT,
    user_prompt=RU_SEARCHSCLS_USER_PROMPT,
    assistant_prompt=RU_SEARCHSCLS_ASSISTANT_PROMPT,
    parse_answer_func=searchscls_custom_parse
)

SEARCHSCLS_SUITE_V3 = {'ru': RU_SEARCHSCLS_SUITE, 'en': EN_SEARCHSCLS_SUITE}
