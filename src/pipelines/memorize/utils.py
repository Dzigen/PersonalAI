from dataclasses import dataclass
from ..utils import BaseStages
from .extractor import LLMExtractor
from .updator import LLMUpdator


@dataclass
class MemPipelineStages(BaseStages):
    """Класс определяет набор стадий Memorize-конвейера.

    :param extractor: Компонента, отвечающая за извлечение структурированной информации (триплетов) из исходного текста.
    :type extractor: LLMExtractor
    :param updator: Компонента, отвечающая за обновление/актуализацию знаний в памяти (графе знаний) ассистента.
    :type updator: LLMUpdator
    """
    extractor: LLMExtractor
    updator: LLMUpdator
