from .........utils import AgentTaskSuite

from .parsers import canswgen_custom_parse

from .prompts import EN_CANSWGEN_SYSTEM_PROMPT, EN_CANSWGEN_USER_PROMPT, EN_CANSWGEN_ASSISTANT_PROMPT, \
    RU_CANSWGEN_SYSTEM_PROMPT, RU_CANSWGEN_USER_PROMPT, RU_CANSWGEN_ASSISTANT_PROMPT

EN_CANSWGEN_SUITE = AgentTaskSuite(
    system_prompt=EN_CANSWGEN_SYSTEM_PROMPT,
    user_prompt=EN_CANSWGEN_USER_PROMPT,
    assistant_prompt=EN_CANSWGEN_ASSISTANT_PROMPT,
    parse_answer_func=canswgen_custom_parse
)

RU_CANSWGEN_SUITE = AgentTaskSuite(
    system_prompt=RU_CANSWGEN_SYSTEM_PROMPT,
    user_prompt=RU_CANSWGEN_USER_PROMPT,
    assistant_prompt=RU_CANSWGEN_ASSISTANT_PROMPT,
    parse_answer_func=canswgen_custom_parse
)

CANSWGEN_SUITE_V2 = {'ru': RU_CANSWGEN_SUITE, 'en': EN_CANSWGEN_SUITE}
