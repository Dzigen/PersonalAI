from dataclasses import dataclass, field
from typing import Dict

from ...prompts.query_parser import ENTITIES_EXTRACTION_EN_USER_PROMPT, ENTITIES_EXTRACTION_RU_USER_PROMPT
from ...prompts.system import RU_SYSTEM_PROMPT, EN_SYSTEM_PROMPT
from ...parsers.query_parser import qa_custom_entities_parse_func

QP_LOG_PATH = 'log/qp'

ENTITIES_EXTRACTION_USER_PROMPT = {
    'ru': ENTITIES_EXTRACTION_RU_USER_PROMPT,
    'en': ENTITIES_EXTRACTION_EN_USER_PROMPT
}

ENTITIES_EXTRACTION_SYSTEM_PROMPT = {
    'ru': RU_SYSTEM_PROMPT,
    'en': EN_SYSTEM_PROMPT
}

ENTITIES_PARSE_FUNC = {
    'ru': qa_custom_entities_parse_func,
    'en': qa_custom_entities_parse_func
}

@dataclass
class EntitiesExtractorConfig:
    """Конфигурация алгоритма по извлечению ключевых сущностей из текста.

    :param user_prompt: User-промпт для LLM-агента с описанием задачи по извлечению ключевых сущностей из текста.
    :type user_prompt: Dict
    :param system_prompt: System-промпт с описание персоны, свойствам которой должен удовлетворять LLM-агент при генерации оветов.
    :param entities_parse_func: Функция разбора результатов генерации LLM-агента.
    :type entities_parse_func: Dict
    """
    user_prompt: Dict = field(default_factory=lambda: ENTITIES_EXTRACTION_USER_PROMPT)
    system_prompt: Dict = field(default_factory=lambda: ENTITIES_EXTRACTION_SYSTEM_PROMPT)
    entities_parse_func: Dict = field(default_factory=lambda: ENTITIES_PARSE_FUNC)
