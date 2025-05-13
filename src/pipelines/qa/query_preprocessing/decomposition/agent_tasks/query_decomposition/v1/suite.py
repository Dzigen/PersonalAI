from ........utils import AgentTaskSuite

from .parsers import qd_custom_answer_parse

from .prompts import EN_QDECOMP_SYSTEM_PROMPT, EN_QDECOMP_USER_PROMPT, EN_QDECOMP_ASSISTANT_PROMPT, \
        RU_QDECOMP_SYSTEM_PROMPT, RU_QDECOMP_USER_PROMPT, RU_QDECOMP_ASSISTANT_PROMPT

EN_QDECOMP_SUITE = AgentTaskSuite(
    system_prompt=EN_QDECOMP_SYSTEM_PROMPT,
    user_prompt=EN_QDECOMP_USER_PROMPT,
    assistant_prompt=EN_QDECOMP_ASSISTANT_PROMPT,
    parse_answer_func=qd_custom_answer_parse
)

RU_QDECOMP_SUITE = AgentTaskSuite(
    system_prompt=RU_QDECOMP_SYSTEM_PROMPT,
    user_prompt=RU_QDECOMP_USER_PROMPT,
    assistant_prompt=RU_QDECOMP_ASSISTANT_PROMPT,
    parse_answer_func=qd_custom_answer_parse
)

QUERY_DECOMP_SUITE_V1 = {'ru': RU_QDECOMP_SUITE, 'en': EN_QDECOMP_SUITE}
