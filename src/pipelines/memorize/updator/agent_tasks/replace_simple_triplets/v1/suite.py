from .parsers import rs_custom_parse, rs_custom_postprocess, rs_custom_formate
from .prompts import RU_REPLACE_SIMPLE_USER_PROMPT, EN_REPLACE_SIMPLE_USER_PROMPT, \
    RU_REPLACE_SIMPLE_SYSTEM_PROMPT, EN_REPLACE_SIMPLE_SYSTEM_PROMPT

from .......utils import AgentTaskSuite

EN_REPLACE_SIMPLE_SUITE = AgentTaskSuite(
    system_prompt=EN_REPLACE_SIMPLE_SYSTEM_PROMPT,
    user_prompt=EN_REPLACE_SIMPLE_USER_PROMPT,
    assistant_prompt=None,
    parse_answer_func=rs_custom_parse,
    postprocess_answer_func=rs_custom_postprocess
)

RU_REPLACE_SIMPLE_SUITE = AgentTaskSuite(
    system_prompt=RU_REPLACE_SIMPLE_SYSTEM_PROMPT,
    user_prompt=RU_REPLACE_SIMPLE_USER_PROMPT,
    assistant_prompt=None,
    parse_answer_func=rs_custom_parse,
    postprocess_answer_func=rs_custom_postprocess
)

REPLACE_SIMPLE_SUITE = {'ru': RU_REPLACE_SIMPLE_SUITE, 'en': EN_REPLACE_SIMPLE_SUITE}

REPLACE_SIMPLE_TASK_CONFIGV1 = {
    'suites': REPLACE_SIMPLE_SUITE,
    'custom_formate': rs_custom_formate
}
