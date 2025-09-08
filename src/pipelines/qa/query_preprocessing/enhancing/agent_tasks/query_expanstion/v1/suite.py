from ........utils import AgentTaskSuite

from .parsers import qexpan_custom_parse

from .prompts import EN_QEXPAN_SYSTEM_PROMPT, EN_QEXPAN_USER_PROMPT, EN_QEXPAN_ASSISTANT_PROMPT, \
    RU_QEXPAN_SYSTEM_PROMPT, RU_QEXPAN_USER_PROMPT, RU_QEXPAN_ASSISTANT_PROMPT

EN_QEXPAN_SUITE = AgentTaskSuite(
    system_prompt=EN_QEXPAN_SYSTEM_PROMPT,
    user_prompt=EN_QEXPAN_USER_PROMPT,
    assistant_prompt=EN_QEXPAN_ASSISTANT_PROMPT,
    parse_answer_func=qexpan_custom_parse
)

RU_QEXPAN_SUITE = AgentTaskSuite(
    system_prompt=RU_QEXPAN_SYSTEM_PROMPT,
    user_prompt=RU_QEXPAN_USER_PROMPT,
    assistant_prompt=RU_QEXPAN_ASSISTANT_PROMPT,
    parse_answer_func=qexpan_custom_parse
)

QEXPAN_SUITE_V1 = {'ru': RU_QEXPAN_SUITE, 'en': EN_QEXPAN_SUITE}
