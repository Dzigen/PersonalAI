from dataclasses import dataclass
from typing import Union

from ..utils import BaseStages
from .answer_generator import QALLMGenerator
from .knowledge_retriever import KnowledgeRetriever
from .knowledge_comparator import KnowledgeComparator
from .query_parser import QueryLLMParser


@dataclass
class WeakKGReasonerStages(BaseStages):
    knowledge_retriever: KnowledgeRetriever
    answer_generator: QALLMGenerator
    query_parser: Union[QueryLLMParser, None] = None
    knowledge_comparator: Union[KnowledgeComparator, None] = None
