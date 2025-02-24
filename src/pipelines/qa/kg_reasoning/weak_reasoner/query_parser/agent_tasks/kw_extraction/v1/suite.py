from .........utils import AgentTaskSuite

from .prompts import \
    EN_KW_EXTRACTION_SYSTEM_PROMPT, EN_KW_EXTRACTION_USER_PROMPT, \
        RU_KW_EXTRACTION_SYSTEM_PROMPT, RU_KW_EXTRACTION_USER_PROMPT

from .parsers import kwe_custom_formate, kwe_custom_parse, kwe_custom_postprocess

EN_KW_EXTRACTION_SUITE = AgentTaskSuite(
    system_prompt=EN_KW_EXTRACTION_SYSTEM_PROMPT,
    user_prompt=EN_KW_EXTRACTION_USER_PROMPT,
    assistant_prompt=None,
    parse_answer_func=kwe_custom_parse,
    postprocess_answer_func=kwe_custom_postprocess
)

RU_KW_EXTRACTION_SUITE = AgentTaskSuite(
    system_prompt=RU_KW_EXTRACTION_SYSTEM_PROMPT,
    user_prompt=RU_KW_EXTRACTION_USER_PROMPT,
    assistant_prompt=None,
    parse_answer_func=kwe_custom_parse,
    postprocess_answer_func=kwe_custom_postprocess
)

KWE_GEN_SUITE = {'ru': RU_KW_EXTRACTION_SUITE, 'en': EN_KW_EXTRACTION_SUITE}

KWE_TASK_CONFIGV1 = {
    'suites': KWE_GEN_SUITE,
    'custom_formate': kwe_custom_formate
}
