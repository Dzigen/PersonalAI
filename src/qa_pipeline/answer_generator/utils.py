from ...prompts.question_answering import QA_EN_USER_PROMPT, QA_RU_USER_PROMPT
from ...prompts.system import RU_SYSTEM_PROMPT, EN_SYSTEM_PROMPT
from ...parsers.question_answering import qa_custom_answer_parse_func_ru, qa_custom_answer_parse_func_en

QA_LOG_PATH = 'log/raw_qa'

#
QA_USER_PROMPT = {
    'ru': QA_RU_USER_PROMPT,
    'en': QA_EN_USER_PROMPT}

#
QA_SYSTEM_PROMPT = {
    'ru': RU_SYSTEM_PROMPT,
    'en': EN_SYSTEM_PROMPT}

#
ANSWER_PARSE_FUNC = {
    'ru': qa_custom_answer_parse_func_ru,
    'en': qa_custom_answer_parse_func_en
}
