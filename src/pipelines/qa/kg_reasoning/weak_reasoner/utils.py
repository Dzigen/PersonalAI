from dataclasses import dataclass
from typing import Union

from .answer_generator import QALLMGenerator
from .knowledge_comparator import KnowledgeComparator
from .query_parser import QueryLLMParser
from ..utils import BaseStages
from ...knowledge_retriever import KnowledgeRetriever


@dataclass
class WeakKGReasonerStages(BaseStages):
    """Контейнер стадий weak-reasoner пайплайна.

    :param knowledge_retriever: Извлечение релевантных триплетов из графа знаний.
    :type knowledge_retriever: KnowledgeRetriever
    :param answer_generator: Генерация итогового ответа по найденным фактам.
    :type answer_generator: QALLMGenerator
    :param query_parser: Парсер запроса для извлечения.
    :type query_parser: Union[QueryLLMParser, None]
    :param knowledge_comparator: Сопоставление сущностей с узлами графа.
    :type knowledge_comparator: Union[KnowledgeComparator, None]
    """
    knowledge_retriever: KnowledgeRetriever
    answer_generator: QALLMGenerator
    query_parser: Union[QueryLLMParser, None] = None
    knowledge_comparator: Union[KnowledgeComparator, None] = None
