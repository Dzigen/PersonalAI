from dataclasses import dataclass, field

from .query_parser import QueryLLMParserConfig
from .knowledge_comparator import KnowledgeComparatorConfig
from .knowledge_retriever import KnowledgeRetrieverConfig
from .answer_generator import QALLMGeneratorConfig

@dataclass
class QAPipelineConfig:
    knowledge_retriever_config: KnowledgeRetrieverConfig = field(default_factory=lambda: KnowledgeRetrieverConfig())
    query_parser_config: QueryLLMParserConfig = field(default_factory=lambda: QueryLLMParserConfig())
    knowledge_comparator_config: KnowledgeComparatorConfig = field(default_factory=lambda: KnowledgeComparatorConfig())
    answer_generator_config: QALLMGeneratorConfig = field(default_factory=lambda: QALLMGeneratorConfig())