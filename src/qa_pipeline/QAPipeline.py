from .answer_generator import QALLMGenerator, QALLMGeneratorConfig
from .knowledge_retriever import KnowledgeRetriever, KnowledgeRetrieverConfig
from .knowledge_comparator import KnowledgeComparator, KnowledgeComparatorConfig
from .query_parser import QueryLLMParser, QueryLLMParserConfig
from .utils import LOG_PATH
from ..agents.private import GigaChatAgent
from ..knowledge_graph_model import KnowledgeGraphModel
from ..utils import Logger

from dataclasses import dataclass, field

@dataclass
class QAPipelineConfig:
    query_parser_config: QueryLLMParserConfig = field(default_factory=lambda: QueryLLMParserConfig())
    knowledge_comparator_config: KnowledgeComparatorConfig = field(default_factory=lambda: KnowledgeComparatorConfig())
    knowledge_retriever_config: KnowledgeRetrieverConfig = field(default_factory=lambda: KnowledgeRetrieverConfig())
    answer_generator_config: QALLMGeneratorConfig = field(default_factory=lambda: QALLMGeneratorConfig())
    log: Logger = field(default_factory=lambda: Logger(LOG_PATH))
    verbose: bool = False

class QAPipeline:
    """Главный класс QA-конвейера для генерации ответов на пользовательские вопросы
    с использованием имеющегося графа знаний
    """

    def __init__(self, kg_model: KnowledgeGraphModel, config: QAPipelineConfig = QAPipelineConfig()) -> None:
        self.config = config
        self.kg_model = kg_model
        self.log = config.log

        self.query_parser = QueryLLMParser(self.config.query_parser_config)
        self.knowledge_comparator = KnowledgeComparator(self.kg_model, self.config.knowledge_comparator_config)
        self.knowledge_retriever = KnowledgeRetriever(self.kg_model, self.config.knowledge_retriever_config)
        self.answer_generator = QALLMGenerator(self.config.answer_generator_config)

    def answer(self, query: str) -> str:
        self.log("=STAGE#1 - entities extraction", verbose=self.config.verbose)
        query_info = self.query_parser.extract_entities(query)
        self.log("EXTRACTED_ENTITIES:\n" + ', '.join(query_info.entities), verbose=self.config.verbose)
        
        self.log("=STAGE#2 - kg_nodes to query linking", verbose=self.config.verbose)
        self.knowledge_comparator.link_kgnodes_to_query(query_info)
        self.log("LINKED_NODES:\n" + ', '.join(list(map(lambda v: v.document, query_info.linked_nodes))), verbose=self.config.verbose)
        
        self.log("=STAGE#3 - retrieve", verbose=self.config.verbose)
        retrieved_triplets = self.knowledge_retriever.retrieve(query_info)
        
        self.log("=STAGE#4 - answer generation", verbose=self.config.verbose)
        self.log("QUERY:\n" + query_info.query, verbose=self.config.verbose)
        context = self.answer_generator.formate_context(retrieved_triplets)
        self.log("CONTEXT:\n" + context, verbose=self.config.verbose)
        answer = self.answer_generator.generate(query_info.query, context)
        self.log("ANSWER: " + answer, verbose=self.config.verbose)

        return answer