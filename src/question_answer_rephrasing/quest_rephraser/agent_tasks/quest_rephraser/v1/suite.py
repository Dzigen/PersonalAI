from src.utils import AgentTaskSuite

from .parsers import quest_reph_custom_answer_parse
from .prompts import \
    EN_QUEST_REPH_SYSTEM_PROMPT, EN_QUEST_REPH_USER_PROMPT, EN_QUEST_REPH_ASSISTANT_PROMPT, \
    RU_QUEST_REPH_SYSTEM_PROMPT, RU_QUEST_REPH_USER_PROMPT, RU_QUEST_REPH_ASSISTANT_PROMPT


EN_QUEST_REPH_SUITE = AgentTaskSuite(
    system_prompt=EN_QUEST_REPH_SYSTEM_PROMPT,
    user_prompt=EN_QUEST_REPH_USER_PROMPT,
    assistant_prompt=EN_QUEST_REPH_ASSISTANT_PROMPT,
    parse_answer_func=quest_reph_custom_answer_parse
)

RU_QUEST_REPH_SUITE = AgentTaskSuite(
    system_prompt=RU_QUEST_REPH_SYSTEM_PROMPT,
    user_prompt=RU_QUEST_REPH_USER_PROMPT,
    assistant_prompt=RU_QUEST_REPH_ASSISTANT_PROMPT,
    parse_answer_func=quest_reph_custom_answer_parse
)

QUEST_REPH_SUITE_V1 = {
    'ru': RU_QUEST_REPH_SUITE, 'en': EN_QUEST_REPH_SUITE}
