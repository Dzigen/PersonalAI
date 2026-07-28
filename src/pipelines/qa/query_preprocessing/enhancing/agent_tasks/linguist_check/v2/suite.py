from ........utils import AgentTaskSuite

from .parsers import lcheck_custom_parse

from .prompts import EN_LCHECK_SYSTEM_PROMPT, EN_LCHECK_USER_PROMPT, EN_LCHECK_ASSISTANT_PROMPT, \
    RU_LCHECK_SYSTEM_PROMPT, RU_LCHECK_USER_PROMPT, RU_LCHECK_ASSISTANT_PROMPT

EN_LCHECK_SUITE = AgentTaskSuite(
    system_prompt=EN_LCHECK_SYSTEM_PROMPT,
    user_prompt=EN_LCHECK_USER_PROMPT,
    assistant_prompt=EN_LCHECK_ASSISTANT_PROMPT,
    parse_answer_func=lcheck_custom_parse
)

RU_LCHECK_SUITE = AgentTaskSuite(
    system_prompt=RU_LCHECK_SYSTEM_PROMPT,
    user_prompt=RU_LCHECK_USER_PROMPT,
    assistant_prompt=RU_LCHECK_ASSISTANT_PROMPT,
    parse_answer_func=lcheck_custom_parse
)

LCHECK_SUITE_V2 = {'ru': RU_LCHECK_SUITE, 'en': EN_LCHECK_SUITE}
