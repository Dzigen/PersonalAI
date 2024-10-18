from dataclasses import dataclass

from ...prompts.query_parser import ENTITIES_EXTRACTION_EN_USER_PROMPT, ENTITIES_EXTRACTION_RU_USER_PROMPT
from ...prompts.system import RU_SYSTEM_PROMPT, EN_SYSTEM_PROMPT

QP_LOG_PATH = 'log/qp'

ENTITIES_EXTRACTION_USER_PROMPT = {
    'ru': ENTITIES_EXTRACTION_RU_USER_PROMPT,
    'en:': ENTITIES_EXTRACTION_EN_USER_PROMPT
}

ENTITIES_EXTRACTION_SYSTEM_PROMPT = {
    'ru': RU_SYSTEM_PROMPT,
    'en:': EN_SYSTEM_PROMPT
}


@dataclass
class EntitiesExtractorConfig:
    user_prompt: str = ENTITIES_EXTRACTION_USER_PROMPT

