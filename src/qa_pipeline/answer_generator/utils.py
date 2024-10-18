from ...prompts.question_answering import QA_EN_USER_PROMPT, QA_RU_USER_PROMPT
from ...prompts.system import RU_SYSTEM_PROMPT, EN_SYSTEM_PROMPT

QA_LOG_PATH = 'log/raw_qa'

QA_USER_PROMPT = {
    'ru': QA_RU_USER_PROMPT,
    'en': QA_EN_USER_PROMPT}

QA_SYSTEM_PROMPT = {
    'ru': RU_SYSTEM_PROMPT,
    'en': EN_SYSTEM_PROMPT}