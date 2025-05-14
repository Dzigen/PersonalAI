from .........utils import AgentTaskSuite

from .parsers import qgen_custom_parse
from .prompts import EN_QGEN_SYSTEM_PROMPT, EN_QGEN_USER_PROMPT, EN_QGEN_ASSISTANT_PROMPT, \
        RU_QGEN_SYSTEM_PROMPT, RU_QGEN_USER_PROMPT, RU_QGEN_ASSISTANT_PROMPT

EN_QGEN_SUITE = AgentTaskSuite(
    system_prompt=EN_QGEN_SYSTEM_PROMPT,
    user_prompt=EN_QGEN_USER_PROMPT,
    assistant_prompt=EN_QGEN_ASSISTANT_PROMPT,
    parse_answer_func=qgen_custom_parse
)

RU_QGEN_SUITE = AgentTaskSuite(
    system_prompt=RU_QGEN_SYSTEM_PROMPT,
    user_prompt=RU_QGEN_USER_PROMPT,
    assistant_prompt=RU_QGEN_ASSISTANT_PROMPT,
    parse_answer_func=qgen_custom_parse
)

QGEN_SUITE_V1 = {'ru': RU_QGEN_SUITE, 'en': EN_QGEN_SUITE}