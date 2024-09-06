from dataclasses import dataclass

from .query_parser import QueryLLMParserConfig
from .knowledge_comparator import KnowledgeComparatorConfig
from .knowledge_retriever import KnowledgeRetrieverConfig
from .answer_generator import QALLMGeneratorConfig

@dataclass
class QAPipelineConfig:
    query_parser_config: QueryLLMParserConfig
    knowledge_comparator_config: KnowledgeComparatorConfig
    knowledge_retriever_config: KnowledgeRetrieverConfig
    answer_generator_config: QALLMGeneratorConfig