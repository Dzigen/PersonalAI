from .......utils import AgentTaskSuite

from .parsers import csubasumm_custom_answer_parse

from .prompts import EN_CSUBASUMM_SYSTEM_PROMPT, EN_CSUBASUMM_USER_PROMPT, EN_CSUBASUMM_ASSISTANT_PROMPT, \
    RU_CSUBASUMM_SYSTEM_PROMPT, RU_CSUBASUMM_USER_PROMPT, RU_CSUBASUMM_ASSISTANT_PROMPT

EN_CSUBASUMM_SUITE = AgentTaskSuite(
    system_prompt=EN_CSUBASUMM_SYSTEM_PROMPT,
    user_prompt=EN_CSUBASUMM_USER_PROMPT,
    assistant_prompt=EN_CSUBASUMM_ASSISTANT_PROMPT,
    parse_answer_func=csubasumm_custom_answer_parse
)

RU_CSUBASUMM_SUITE = AgentTaskSuite(
    system_prompt=RU_CSUBASUMM_SYSTEM_PROMPT,
    user_prompt=RU_CSUBASUMM_USER_PROMPT,
    assistant_prompt=RU_CSUBASUMM_ASSISTANT_PROMPT,
    parse_answer_func=csubasumm_custom_answer_parse
)

CSUBASUMM_SUITE_V2 = {'ru': RU_CSUBASUMM_SUITE, 'en': EN_CSUBASUMM_SUITE}
