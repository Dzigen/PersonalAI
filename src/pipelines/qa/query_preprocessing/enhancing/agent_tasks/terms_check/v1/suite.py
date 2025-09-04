from ........utils import AgentTaskSuite

from .parsers import tcheck_custom_parse

from .prompts import EN_TCHECK_SYSTEM_PROMPT, EN_TCHECK_USER_PROMPT, EN_TCHECK_ASSISTANT_PROMPT, \
        RU_TCHECK_SYSTEM_PROMPT, RU_TCHECK_USER_PROMPT, RU_TCHECK_ASSISTANT_PROMPT

EN_TCHECK_SUITE = AgentTaskSuite(
    system_prompt=EN_TCHECK_SYSTEM_PROMPT,
    user_prompt=EN_TCHECK_USER_PROMPT,
    assistant_prompt=EN_TCHECK_ASSISTANT_PROMPT,
    parse_answer_func=tcheck_custom_parse
)

RU_TCHECK_SUITE = AgentTaskSuite(
    system_prompt=RU_TCHECK_SYSTEM_PROMPT,
    user_prompt=RU_TCHECK_USER_PROMPT,
    assistant_prompt=RU_TCHECK_ASSISTANT_PROMPT,
    parse_answer_func=tcheck_custom_parse
)

TCHECK_SUITE_V1 = {'ru': RU_TCHECK_SUITE, 'en': EN_TCHECK_SUITE}
