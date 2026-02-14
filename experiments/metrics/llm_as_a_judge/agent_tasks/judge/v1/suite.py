from .parsers import llmjudge_custom_parse
from .prompts import \
    EN_LLMJ_SYSTEM_PROMPT, EN_LLMJ_USER_PROMPT, EN_LLMJ_ASSISTANT_PROMPT, \
    RU_LLMJ_SYSTEM_PROMPT, RU_LLMJ_USER_PROMPT, RU_LLMJ_ASSISTANT_PROMPT
from src.utils import AgentTaskSuite
import sys
BASE_PATH = '../'  # TO CHANGE
sys.path.insert(0, BASE_PATH)


EN_LLMJUDGE_SUITE = AgentTaskSuite(
    system_prompt=EN_LLMJ_SYSTEM_PROMPT,
    user_prompt=EN_LLMJ_USER_PROMPT,
    assistant_prompt=EN_LLMJ_ASSISTANT_PROMPT,
    parse_answer_func=llmjudge_custom_parse
)

RU_LLMJUDGE_SUITE = AgentTaskSuite(
    system_prompt=RU_LLMJ_SYSTEM_PROMPT,
    user_prompt=RU_LLMJ_USER_PROMPT,
    assistant_prompt=RU_LLMJ_ASSISTANT_PROMPT,
    parse_answer_func=llmjudge_custom_parse
)

LLMJUDGE_SUITE_V1 = {'ru': RU_LLMJUDGE_SUITE, 'en': EN_LLMJUDGE_SUITE}
