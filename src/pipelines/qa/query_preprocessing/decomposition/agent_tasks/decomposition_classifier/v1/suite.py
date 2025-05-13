from ........utils import AgentTaskSuite

from .parsers import dc_custom_answer_parse
from .prompts import EN_DCLS_SYSTEM_PROMPT, EN_DCLS_USER_PROMPT, EN_DCLS_ASSISTANT_PROMPT, \
        RU_DCLS_SYSTEM_PROMPT, RU_DCLS_USER_PROMPT, RU_DCLS_ASSISTANT_PROMPT

EN_DCLS_SUITE = AgentTaskSuite(
    system_prompt=EN_DCLS_SYSTEM_PROMPT,
    user_prompt=EN_DCLS_USER_PROMPT,
    assistant_prompt=EN_DCLS_ASSISTANT_PROMPT,
    parse_answer_func=dc_custom_answer_parse
)

RU_DCLS_SUITE = AgentTaskSuite(
    system_prompt=RU_DCLS_SYSTEM_PROMPT,
    user_prompt=RU_DCLS_USER_PROMPT,
    assistant_prompt=RU_DCLS_ASSISTANT_PROMPT,
    parse_answer_func=dc_custom_answer_parse
)

DECOMP_CLS_SUITE_V1 = {'ru': RU_DCLS_SUITE, 'en': EN_DCLS_SUITE}
