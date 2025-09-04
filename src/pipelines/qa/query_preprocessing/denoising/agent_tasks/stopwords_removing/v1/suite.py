from ........utils import AgentTaskSuite

from .parsers import swremv_custom_parse

from .prompts import EN_SWREMV_SYSTEM_PROMPT, EN_SWREMV_USER_PROMPT, EN_SWREMV_ASSISTANT_PROMPT, \
        RU_SWREMV_SYSTEM_PROMPT, RU_SWREMV_USER_PROMPT, RU_SWREMV_ASSISTANT_PROMPT

EN_SWREMV_SUITE = AgentTaskSuite(
    system_prompt=EN_SWREMV_SYSTEM_PROMPT,
    user_prompt=EN_SWREMV_USER_PROMPT,
    assistant_prompt=EN_SWREMV_ASSISTANT_PROMPT,
    parse_answer_func=swremv_custom_parse
)

RU_SWREMV_SUITE = AgentTaskSuite(
    system_prompt=RU_SWREMV_SYSTEM_PROMPT,
    user_prompt=RU_SWREMV_USER_PROMPT,
    assistant_prompt=RU_SWREMV_ASSISTANT_PROMPT,
    parse_answer_func=swremv_custom_parse
)

SWREMV_SUITE_V1 = {'ru': RU_SWREMV_SUITE, 'en': EN_SWREMV_SUITE}
