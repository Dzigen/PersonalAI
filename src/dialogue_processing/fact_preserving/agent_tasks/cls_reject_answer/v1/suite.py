from src.utils import AgentTaskSuite

from .parsers import rjansw_clf_custom_answer_parse
from .prompts import \
    EN_REJECT_ANSW_CLS_SYSTEM_PROMPT, EN_REJECT_ANSW_CLS_USER_PROMPT, EN_REJECT_ANSW_CLS_ASSISTANT_PROMPT, \
    RU_REJECT_ANSW_CLS_SYSTEM_PROMPT, RU_REJECT_ANSW_CLS_USER_PROMPT, RU_REJECT_ANSW_CLS_ASSISTANT_PROMPT


EN_REJECT_ANSW_CLS_SUITE = AgentTaskSuite(
    system_prompt=EN_REJECT_ANSW_CLS_SYSTEM_PROMPT,
    user_prompt=EN_REJECT_ANSW_CLS_USER_PROMPT,
    assistant_prompt=EN_REJECT_ANSW_CLS_ASSISTANT_PROMPT,
    parse_answer_func=rjansw_clf_custom_answer_parse
)

RU_REJECT_ANSW_CLS_SUITE = AgentTaskSuite(
    system_prompt=RU_REJECT_ANSW_CLS_SYSTEM_PROMPT,
    user_prompt=RU_REJECT_ANSW_CLS_USER_PROMPT,
    assistant_prompt=RU_REJECT_ANSW_CLS_ASSISTANT_PROMPT,
    parse_answer_func=rjansw_clf_custom_answer_parse
)

REJECT_ANSW_CLS_SUITE_V1 = {
    'ru': RU_REJECT_ANSW_CLS_SUITE, 'en': EN_REJECT_ANSW_CLS_SUITE}
