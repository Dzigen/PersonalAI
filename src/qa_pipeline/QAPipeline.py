from .answer_generator import QALLMGenerator, QALLMGeneratorConfig
from .knowledge_retriever import KnowledgeRetriever, KnowledgeRetrieverConfig
from .knowledge_comparator import KnowledgeComparator, KnowledgeComparatorConfig
from .query_parser import QueryLLMParser, QueryLLMParserConfig
from .utils import LOG_PATH
from ..knowledge_graph_model import KnowledgeGraphModel
from ..utils import Logger, ReturnStatus, ReturnInfo

from dataclasses import dataclass, field
from typing import Tuple

@dataclass
class QAPipelineConfig:
    #
    query_parser_config: QueryLLMParserConfig = field(default_factory=lambda: QueryLLMParserConfig())
    #
    knowledge_comparator_config: KnowledgeComparatorConfig = field(default_factory=lambda: KnowledgeComparatorConfig())
    #
    knowledge_retriever_config: KnowledgeRetrieverConfig = field(default_factory=lambda: KnowledgeRetrieverConfig())
    #
    answer_generator_config: QALLMGeneratorConfig = field(default_factory=lambda: QALLMGeneratorConfig())
    #
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

    def answer(self, query: str) -> Tuple[str, ReturnInfo]:
        """_summary_

        :param query: _description_
        :type query: str
        :return: _description_
        :rtype: Tuple[str, ReturnInfo]
        """
        answer = None
        self.log("==="*4 + "STAGE#1 - entities extraction" + "==="*4, verbose=self.config.verbose)
        query_info, info = self.query_parser.extract_entities(query)
        self.log("EXTRACTED_ENTITIES:\n" + ', '.join(query_info.entities), verbose=self.config.verbose)

        if info.status == ReturnStatus.success:
            self.log("==="*4 + "STAGE#2 - kg_nodes to query linking" + "==="*4, verbose=self.config.verbose)
            info = self.knowledge_comparator.link_kgnodes_to_query(query_info)
            self.log("LINKED_NODES:\n" + ', '.join(list(map(lambda v: v.document, query_info.linked_nodes))), verbose=self.config.verbose)

        if info.status == ReturnStatus.success:
            self.log("==="*4 + "STAGE#3 - retrieve" + "==="*4, verbose=self.config.verbose)
            retrieved_triplets, info = self.knowledge_retriever.retrieve(query_info)
            #self.log(f"RETRIEVED_TRIPLES:\n {retrieved_triplets}", verbose=self.config.verbose)

        if info.status == ReturnStatus.success:
            self.log("==="*4 + "STAGE#4 - answer generation" + "==="*4, verbose=self.config.verbose)
            self.log("QUERY:\n" + query_info.query, verbose=self.config.verbose)
            context = self.answer_generator.formate_context(retrieved_triplets)
            self.log("CONTEXT:\n" + context, verbose=self.config.verbose)
            answer, info = self.answer_generator.generate(query_info.query, context)
            self.log("ANSWER: " + answer, verbose=self.config.verbose)

        if info.status != ReturnStatus.success:
            self.log(f"{info.status}: {info.message}", verbose=self.config.verbose)

        return answer, info
