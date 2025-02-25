from .........utils import AgentTaskSuite

from .prompts import \
    EN_KW_EXTRACTION_SYSTEM_PROMPT, EN_KW_EXTRACTION_USER_PROMPT, EN_KW_EXTRACTION_ASSISTANT_PROMPT,\
        RU_KW_EXTRACTION_SYSTEM_PROMPT, RU_KW_EXTRACTION_USER_PROMPT, RU_KW_EXTRACTION_ASSISTANT_PROMPT

from .parsers import kwe_custom_parse

EN_KW_EXTRACTION_SUITE = AgentTaskSuite(
    system_prompt=EN_KW_EXTRACTION_SYSTEM_PROMPT,
    user_prompt=EN_KW_EXTRACTION_USER_PROMPT,
    assistant_prompt=EN_KW_EXTRACTION_ASSISTANT_PROMPT,
    parse_answer_func=kwe_custom_parse
)

RU_KW_EXTRACTION_SUITE = AgentTaskSuite(
    system_prompt=RU_KW_EXTRACTION_SYSTEM_PROMPT,
    user_prompt=RU_KW_EXTRACTION_USER_PROMPT,
    assistant_prompt=RU_KW_EXTRACTION_ASSISTANT_PROMPT,
    parse_answer_func=kwe_custom_parse
)

KWE_GEN_SUITE_V2 = {'ru': RU_KW_EXTRACTION_SUITE, 'en': EN_KW_EXTRACTION_SUITE}
