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
    #: Конфигурация первой стадии QA-конвейера: извлечение сущностей из user-вопроса
    query_parser_config: QueryLLMParserConfig = field(default_factory=lambda: QueryLLMParserConfig())
    #: Конфигурация второй стадии QA-конвейера: сопоставление (match) сущностей из user-вопроса с информацией в графе знаний
    knowledge_comparator_config: KnowledgeComparatorConfig = field(default_factory=lambda: KnowledgeComparatorConfig())
    #: Конфигурация третьей стадии QA-конвейера: извлечение релевантной информации из графа знаний для user-вопроса
    knowledge_retriever_config: KnowledgeRetrieverConfig = field(default_factory=lambda: KnowledgeRetrieverConfig())
    #: Конфигурация четвёртой стадии QA-конвейера: условная генерация ответа на user-вопрос
    answer_generator_config: QALLMGeneratorConfig = field(default_factory=lambda: QALLMGeneratorConfig())
    #
    log: Logger = field(default_factory=lambda: Logger(LOG_PATH))
    verbose: bool = False

class QAPipeline:
    """Верхнеуровневый класс QA-конвейера, отвечающего за генерацию ответов на вопросы."""

    def __init__(self, kg_model: KnowledgeGraphModel, config: QAPipelineConfig = QAPipelineConfig()) -> None:
        self.config = config
        self.kg_model = kg_model
        self.log = config.log

        self.query_parser = QueryLLMParser(self.config.query_parser_config)
        self.knowledge_comparator = KnowledgeComparator(self.kg_model, self.config.knowledge_comparator_config)
        self.knowledge_retriever = KnowledgeRetriever(self.kg_model, self.config.knowledge_retriever_config)
        self.answer_generator = QALLMGenerator(self.config.answer_generator_config)

    def answer(self, query: str) -> Tuple[str, ReturnInfo]:
        """Метод предназначен для генерации ответа на user-вопрос. Ответ обуславливается на информацию из имеющегося графа знаний.

        :param query: User-вопрос на естественном языке.
        :type query: str
        :return: Кортеж из двух объектов: (1) cгенерированный ответ; (2) статус завершения операции с пояснительной информацией.
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
