from .........utils import AgentTaskSuite

from .parsers import ru_ag_custom_answer_parse, en_ag_custom_answer_parse

from .prompts import EN_AG_SYSTEM_PROMPT, EN_AG_USER_PROMPT, EN_AG_ASSISTANT_PROMPT, \
        RU_AG_SYSTEM_PROMPT, RU_AG_USER_PROMPT, RU_AG_ASSISTANT_PROMPT

EN_ANSWER_GEN_SUITE = AgentTaskSuite(
    system_prompt=EN_AG_SYSTEM_PROMPT,
    user_prompt=EN_AG_USER_PROMPT,
    assistant_prompt=EN_AG_ASSISTANT_PROMPT,
    parse_answer_func=en_ag_custom_answer_parse
)

RU_ANSWER_GEN_SUITE = AgentTaskSuite(
    system_prompt=RU_AG_SYSTEM_PROMPT,
    user_prompt=RU_AG_USER_PROMPT,
    assistant_prompt=RU_AG_ASSISTANT_PROMPT,
    parse_answer_func=ru_ag_custom_answer_parse
)

ANSWER_GEN_SUITE_V2 = {'ru': RU_ANSWER_GEN_SUITE, 'en': EN_ANSWER_GEN_SUITE}
