from ........utils import AgentTaskSuite

from .parsers import gramcheck_custom_parse

from .prompts import EN_GRAMCHECK_SYSTEM_PROMPT, EN_GRAMCHECK_USER_PROMPT, EN_GRAMCHECK_ASSISTANT_PROMPT, \
    RU_GRAMCHECK_SYSTEM_PROMPT, RU_GRAMCHECK_USER_PROMPT, RU_GRAMCHECK_ASSISTANT_PROMPT

EN_GRAMCHECK_SUITE = AgentTaskSuite(
    system_prompt=EN_GRAMCHECK_SYSTEM_PROMPT,
    user_prompt=EN_GRAMCHECK_USER_PROMPT,
    assistant_prompt=EN_GRAMCHECK_ASSISTANT_PROMPT,
    parse_answer_func=gramcheck_custom_parse
)

RU_GRAMCHECK_SUITE = AgentTaskSuite(
    system_prompt=RU_GRAMCHECK_SYSTEM_PROMPT,
    user_prompt=RU_GRAMCHECK_USER_PROMPT,
    assistant_prompt=RU_GRAMCHECK_ASSISTANT_PROMPT,
    parse_answer_func=gramcheck_custom_parse
)

GRAMCHECK_SUITE_V2 = {'ru': RU_GRAMCHECK_SUITE, 'en': EN_GRAMCHECK_SUITE}
