from .......utils import AgentTaskSuite

from .parsers import etriplets_custom_parse, etriplets_custom_formate, etriplets_custom_postprocess
from .prompts import \
    EN_TRIPLETS_EXTRACTION_SYSTEM_PROMPT, EN_TRIPLETS_EXTRACTION_USER_PROMPT, EN_TRIPLETS_ASSISTANT_PROMPT,\
        RU_TRIPLETS_EXTRACTION_SYSTEM_PROMPT, RU_TRIPLETS_EXTRACTION_USER_PROMPT, RU_TRIPLETS_ASSISTANT_PROMPT


EN_TRIPLETS_EXTRACT_SUITE = AgentTaskSuite(
    system_prompt=EN_TRIPLETS_EXTRACTION_SYSTEM_PROMPT,
    user_prompt=EN_TRIPLETS_EXTRACTION_USER_PROMPT,
    assistant_prompt=EN_TRIPLETS_ASSISTANT_PROMPT,
    parse_answer_func=etriplets_custom_parse,
    postprocess_answer_func=etriplets_custom_postprocess
)

RU_TRIPLETS_EXTRACT_SUITE = AgentTaskSuite(
    system_prompt=RU_TRIPLETS_EXTRACTION_SYSTEM_PROMPT,
    user_prompt=RU_TRIPLETS_EXTRACTION_USER_PROMPT,
    assistant_prompt=RU_TRIPLETS_ASSISTANT_PROMPT,
    parse_answer_func=etriplets_custom_parse,
    postprocess_answer_func=etriplets_custom_postprocess
)

TRIPLETS_EXTRACT_SUITE = {'ru': RU_TRIPLETS_EXTRACT_SUITE, 'en': EN_TRIPLETS_EXTRACT_SUITE}

TRIPLETS_EXTRACT_TASK_CONFIGV2 = {
    'suites': TRIPLETS_EXTRACT_SUITE,
    'custom_formate': etriplets_custom_formate
}
