from .answer_generator import QALLMGenerator, QALLMGeneratorConfig
from .knowledge_retriever import KnowledgeRetriever, KnowledgeRetrieverConfig
from .knowledge_comparator import KnowledgeComparator, KnowledgeComparatorConfig
from .query_parser import QueryLLMParser, QueryLLMParserConfig
from ..llm_agent import AgentConnector
from ..knowledge_graph_model import KnowledgeGraphModel

from dataclasses import dataclass, field

@dataclass
class QAPipelineConfig:
    knowledge_retriever_config: KnowledgeRetrieverConfig = field(default_factory=lambda: KnowledgeRetrieverConfig())
    query_parser_config: QueryLLMParserConfig = field(default_factory=lambda: QueryLLMParserConfig())
    knowledge_comparator_config: KnowledgeComparatorConfig = field(default_factory=lambda: KnowledgeComparatorConfig())
    answer_generator_config: QALLMGeneratorConfig = field(default_factory=lambda: QALLMGeneratorConfig())

class QAPipeline:
    """Главный класс QA-конвейера для генерации ответов на пользовательские вопросы
    с использованием имеющегося графа знаний
    """

    def __init__(self, kg_model: KnowledgeGraphModel, llm_agent: AgentConnector, config: QAPipelineConfig) -> None:
        self.kg_model = kg_model
        self.llama_agent = llm_agent
        self.config = config

        self.query_parser = QueryLLMParser(self.llama_agent, self.config.query_parser_config)
        self.knowledge_comparator = KnowledgeComparator(self.kg_model, self.config.knowledge_comparator_config)
        self.knowledge_retriever = KnowledgeRetriever(self.kg_model, self.config.knowledge_retriever_config)
        self.answer_generator = QALLMGenerator(self.llama_agent, self.config.answer_generator_config)

    def answer(self, query: str) -> str:
        # stage 1
        query_info = self.query_parser.extract_entities(query)
        # stage 2
        self.knowledge_comparator.link_kgnodes_to_query(query_info)
        # stage 3
        retrieved_triplets = self.knowledge_retriever.retrieve(query_info)
        # stage 4
        context = self.answer_generator.formate_context(retrieved_triplets)
        answer = self.answer_generator.generate(query_info.query, context)

        return answer