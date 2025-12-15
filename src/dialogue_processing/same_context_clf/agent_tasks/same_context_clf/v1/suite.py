from src.utils import AgentTaskSuite

from .parsers import sctx_clf_custom_answer_parse
from .prompts import \
    EN_SAME_CTX_CLS_SYSTEM_PROMPT, EN_SAME_CTX_CLS_USER_PROMPT, EN_SAME_CTX_CLS_ASSISTANT_PROMPT, \
    RU_SAME_CTX_CLS_SYSTEM_PROMPT, RU_SAME_CTX_CLS_USER_PROMPT, RU_SAME_CTX_CLS_ASSISTANT_PROMPT


EN_SAME_CTX_CLS_SUITE = AgentTaskSuite(
    system_prompt=EN_SAME_CTX_CLS_SYSTEM_PROMPT,
    user_prompt=EN_SAME_CTX_CLS_USER_PROMPT,
    assistant_prompt=EN_SAME_CTX_CLS_ASSISTANT_PROMPT,
    parse_answer_func=sctx_clf_custom_answer_parse
)

RU_SAME_CTX_CLS_SUITE = AgentTaskSuite(
    system_prompt=RU_SAME_CTX_CLS_SYSTEM_PROMPT,
    user_prompt=RU_SAME_CTX_CLS_USER_PROMPT,
    assistant_prompt=RU_SAME_CTX_CLS_ASSISTANT_PROMPT,
    parse_answer_func=sctx_clf_custom_answer_parse
)

SAME_CTX_CLS_SUITE_V1 = {
    'ru': RU_SAME_CTX_CLS_SUITE, 'en': EN_SAME_CTX_CLS_SUITE}
