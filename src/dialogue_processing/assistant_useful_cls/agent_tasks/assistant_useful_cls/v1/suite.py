from src.utils import AgentTaskSuite

from .parsers import au_clf_custom_answer_parse
from .prompts import \
    EN_ASSIST_USE_CLS_SYSTEM_PROMPT, EN_ASSIST_USE_CLS_USER_PROMPT, EN_ASSIST_USE_CLS_ASSISTANT_PROMPT, \
    RU_ASSIST_USE_CLS_SYSTEM_PROMPT, RU_ASSIST_USE_CLS_USER_PROMPT, RU_ASSIST_USE_CLS_ASSISTANT_PROMPT


EN_ASSIST_USE_CLS_SUITE = AgentTaskSuite(
    system_prompt=EN_ASSIST_USE_CLS_SYSTEM_PROMPT,
    user_prompt=EN_ASSIST_USE_CLS_USER_PROMPT,
    assistant_prompt=EN_ASSIST_USE_CLS_ASSISTANT_PROMPT,
    parse_answer_func=au_clf_custom_answer_parse
)

RU_ASSIST_USE_CLS_SUITE = AgentTaskSuite(
    system_prompt=RU_ASSIST_USE_CLS_SYSTEM_PROMPT,
    user_prompt=RU_ASSIST_USE_CLS_USER_PROMPT,
    assistant_prompt=RU_ASSIST_USE_CLS_ASSISTANT_PROMPT,
    parse_answer_func=au_clf_custom_answer_parse
)

ASSIST_USE_CLS_SUITE_V1 = {
    'ru': RU_ASSIST_USE_CLS_SUITE, 'en': EN_ASSIST_USE_CLS_SUITE}
