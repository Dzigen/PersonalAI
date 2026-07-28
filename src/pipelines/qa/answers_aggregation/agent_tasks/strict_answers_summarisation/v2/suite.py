from .......utils import AgentTaskSuite

from .parsers import en_ssubasumm_custom_answer_parse, ru_ssubasumm_custom_answer_parse

from .prompts import EN_SSUBASUMM_SYSTEM_PROMPT, EN_SSUBASUMM_USER_PROMPT, EN_SSUBASUMM_ASSISTANT_PROMPT, \
    RU_SSUBASUMM_SYSTEM_PROMPT, RU_SSUBASUMM_USER_PROMPT, RU_SSUBASUMM_ASSISTANT_PROMPT

EN_SSUBASUMM_SUITE = AgentTaskSuite(
    system_prompt=EN_SSUBASUMM_SYSTEM_PROMPT,
    user_prompt=EN_SSUBASUMM_USER_PROMPT,
    assistant_prompt=EN_SSUBASUMM_ASSISTANT_PROMPT,
    parse_answer_func=en_ssubasumm_custom_answer_parse
)

RU_SSUBASUMM_SUITE = AgentTaskSuite(
    system_prompt=RU_SSUBASUMM_SYSTEM_PROMPT,
    user_prompt=RU_SSUBASUMM_USER_PROMPT,
    assistant_prompt=RU_SSUBASUMM_ASSISTANT_PROMPT,
    parse_answer_func=ru_ssubasumm_custom_answer_parse
)

SSUBASUMM_SUITE_V2 = {'ru': RU_SSUBASUMM_SUITE, 'en': EN_SSUBASUMM_SUITE}
