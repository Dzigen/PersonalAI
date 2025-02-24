from .parsers import rt_custom_parse, rt_custom_postprocess, rt_custom_formate
from .prompts import RU_REPLACE_THESIS_USER_PROMPT, EN_REPLACE_THESIS_USER_PROMPT,\
    RU_REPLACE_THESIS_SYSTEM_PROMPT, EN_REPLACE_THESIS_SYSTEM_PROMPT

from .......utils import AgentTaskSuite

EN_REPLACE_THESIS_SUITE = AgentTaskSuite(
    system_prompt=EN_REPLACE_THESIS_SYSTEM_PROMPT,
    user_prompt=EN_REPLACE_THESIS_USER_PROMPT,
    assistant_prompt=None,
    parse_answer_func=rt_custom_parse,
    postprocess_answer_func=rt_custom_postprocess
)

RU_REPLACE_THESIS_SUITE = AgentTaskSuite(
    system_prompt=RU_REPLACE_THESIS_SYSTEM_PROMPT,
    user_prompt=RU_REPLACE_THESIS_USER_PROMPT,
    assistant_prompt=None,
    parse_answer_func=rt_custom_parse,
    postprocess_answer_func=rt_custom_postprocess
)

REPLACE_THESIS_SUITE = {'ru': RU_REPLACE_THESIS_SUITE, 'en': EN_REPLACE_THESIS_SUITE}

REPLACE_THESIS_TASK_CONFIGV2 = {
    'suites': REPLACE_THESIS_SUITE,
    'custom_formate': rt_custom_formate
}
