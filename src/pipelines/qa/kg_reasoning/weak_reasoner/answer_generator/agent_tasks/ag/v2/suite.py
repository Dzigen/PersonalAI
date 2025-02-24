from .........utils import AgentTaskSuite

from .parsers import ag_custom_formate, ag_custom_postprocess,\
      ru_ag_custom_answer_parse, en_ag_custom_answer_parse

from .prompts import EN_AG_SYSTEM_PROMPT, EN_AG_USER_PROMPT, EN_AG_ASSISTANT_PROMPT, \
        RU_AG_SYSTEM_PROMPT, RU_AG_USER_PROMPT, RU_AG_ASSISTANT_PROMPT

EN_ANSWER_GEN_SUITE = AgentTaskSuite(
    system_prompt=EN_AG_SYSTEM_PROMPT,
    user_prompt=EN_AG_USER_PROMPT,
    assistant_prompt=EN_AG_ASSISTANT_PROMPT,
    parse_answer_func=en_ag_custom_answer_parse,
    postprocess_answer_func=ag_custom_postprocess
)

RU_ANSWER_GEN_SUITE = AgentTaskSuite(
    system_prompt=RU_AG_SYSTEM_PROMPT,
    user_prompt=RU_AG_USER_PROMPT,
    assistant_prompt=RU_AG_ASSISTANT_PROMPT,
    parse_answer_func=ru_ag_custom_answer_parse,
    postprocess_answer_func=ag_custom_postprocess
)

ANSWER_GEN_SUITE = {'ru': RU_ANSWER_GEN_SUITE, 'en': EN_ANSWER_GEN_SUITE}

AG_TASK_CONFIGV2 = {
    'suites': ANSWER_GEN_SUITE,
    'custom_formate': ag_custom_formate
}
