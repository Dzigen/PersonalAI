from src.utils import AgentTaskSuite

from .parsers import fpreserve_custom_parse
from .prompts import \
    EN_FACT_PRESRVE_SYSTEM_PROMPT, EN_FACT_PRESRVE_USER_PROMPT, EN_FACT_PRESRVE_ASSISTANT_PROMPT, \
    RU_FACT_PRESRVE_SYSTEM_PROMPT, RU_FACT_PRESRVE_USER_PROMPT, RU_FACT_PRESRVE_ASSISTANT_PROMPT


EN_FACT_PRESERVE_SUITE = AgentTaskSuite(
    system_prompt=EN_FACT_PRESRVE_SYSTEM_PROMPT,
    user_prompt=EN_FACT_PRESRVE_USER_PROMPT,
    assistant_prompt=EN_FACT_PRESRVE_ASSISTANT_PROMPT,
    parse_answer_func=fpreserve_custom_parse
)

RU_FACT_PRESERVE_SUITE = AgentTaskSuite(
    system_prompt=RU_FACT_PRESRVE_SYSTEM_PROMPT,
    user_prompt=RU_FACT_PRESRVE_USER_PROMPT,
    assistant_prompt=RU_FACT_PRESRVE_ASSISTANT_PROMPT,
    parse_answer_func=fpreserve_custom_parse
)

FACT_PRESERVE_SUITE_V1 = {
    'ru': RU_FACT_PRESERVE_SUITE, 'en': EN_FACT_PRESERVE_SUITE}
