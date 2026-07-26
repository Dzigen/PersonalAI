from .........utils import AgentTaskSuite

from .parsers import sanswgen_custom_parse

from .prompts import EN_SANSWGEN_SYSTEM_PROMPT, EN_SANSWGEN_USER_PROMPT, EN_SANSWGEN_ASSISTANT_PROMPT, \
    RU_SANSWGEN_SYSTEM_PROMPT, RU_SANSWGEN_USER_PROMPT, RU_SANSWGEN_ASSISTANT_PROMPT

EN_SANSWGEN_SUITE = AgentTaskSuite(
    system_prompt=EN_SANSWGEN_SYSTEM_PROMPT,
    user_prompt=EN_SANSWGEN_USER_PROMPT,
    assistant_prompt=EN_SANSWGEN_ASSISTANT_PROMPT,
    parse_answer_func=sanswgen_custom_parse
)

RU_SANSWGEN_SUITE = AgentTaskSuite(
    system_prompt=RU_SANSWGEN_SYSTEM_PROMPT,
    user_prompt=RU_SANSWGEN_USER_PROMPT,
    assistant_prompt=RU_SANSWGEN_ASSISTANT_PROMPT,
    parse_answer_func=sanswgen_custom_parse
)

SANSWGEN_SUITE_V2 = {'ru': RU_SANSWGEN_SUITE, 'en': EN_SANSWGEN_SUITE}
