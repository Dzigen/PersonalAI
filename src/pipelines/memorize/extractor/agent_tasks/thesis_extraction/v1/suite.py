from .......utils import AgentTaskSuite

from .parsers import ethesises_custom_parse, ethesises_custom_formate, ethesises_custom_postprocess
from .prompts import \
    EN_THESISES_EXTRACTION_SYSTEM_PROMPT, EN_THESISES_EXTRACTION_USER_PROMPT, \
        RU_THESISES_EXTRACTION_SYSTEM_PROMPT, RU_THESISES_EXTRACTION_USER_PROMPT


EN_THESISES_EXTRACT_SUITE = AgentTaskSuite(
    system_prompt=EN_THESISES_EXTRACTION_SYSTEM_PROMPT,
    user_prompt=EN_THESISES_EXTRACTION_USER_PROMPT,
    assistant_prompt=None,
    parse_answer_func=ethesises_custom_parse,
    postprocess_answer_func=ethesises_custom_postprocess
)

RU_THESISES_EXTRACT_SUITE = AgentTaskSuite(
    system_prompt=RU_THESISES_EXTRACTION_SYSTEM_PROMPT,
    user_prompt=RU_THESISES_EXTRACTION_USER_PROMPT,
    assistant_prompt=None,
    parse_answer_func=ethesises_custom_parse,
    postprocess_answer_func=ethesises_custom_postprocess
)

THESIS_EXTRACT_SUITE = {'ru': RU_THESISES_EXTRACT_SUITE, 'en': EN_THESISES_EXTRACT_SUITE}

THESIS_EXTRACT_TASK_CONFIGV1 = {
    'suites': THESIS_EXTRACT_SUITE,
    'custom_formate': ethesises_custom_formate
}
