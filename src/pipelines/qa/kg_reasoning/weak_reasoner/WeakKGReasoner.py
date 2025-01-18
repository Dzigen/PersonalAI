from dataclasses import dataclass, field
from typing import Tuple

from .query_parser import QueryLLMParser, QueryLLMParserConfig
from .knowledge_comparator import KnowledgeComparator, KnowledgeComparatorConfig
from .knowledge_retriever import KnowledgeRetriever, KnowledgeRetrieverConfig
from .answer_generator import QALLMGenerator, QALLMGeneratorConfig
from ..utils import AbstractKGReasoner, BaseKGReasonerConfig
from .....utils.data_structs import create_id
from .....utils import Logger, ReturnInfo, ReturnStatus
from .....utils.errors import STATUS_MESSAGE
from .....kg_model import KnowledgeGraphModel

WKGR_MAIN_LOG_PATH = 'log/qa/kg_reasoner/weak/main'

@dataclass
class WeakKGReasonerConfig(BaseKGReasonerConfig):
    query_parser_config: QueryLLMParserConfig = field(default_factory=lambda: QueryLLMParserConfig())
    knowledge_comparator_config: KnowledgeComparatorConfig = field(default_factory=lambda: KnowledgeComparatorConfig())
    knowledge_retriever_config: KnowledgeRetrieverConfig = field(default_factory=lambda: KnowledgeRetrieverConfig())
    answer_generator_config: QALLMGeneratorConfig = field(default_factory=lambda: QALLMGeneratorConfig())
    log: Logger = field(default_factory=lambda: Logger(WKGR_MAIN_LOG_PATH))
    verbose: bool = False

class WeakKGReasoner(AbstractKGReasoner):

    def __init__(self, kg_model: KnowledgeGraphModel, config: WeakKGReasonerConfig = WeakKGReasonerConfig()):
        self.config = config
        self.kg_model = kg_model
        self.log = config.log

        self.query_parser = QueryLLMParser(self.config.query_parser_config)
        self.knowledge_comparator = KnowledgeComparator(self.kg_model, self.config.knowledge_comparator_config)
        self.knowledge_retriever = KnowledgeRetriever(self.kg_model, self.config.knowledge_retriever_config)
        self.answer_generator = QALLMGenerator(self.config.answer_generator_config)

    def perform(self, query: str) -> Tuple[str, ReturnInfo]:
        """Метод предназначен для генерации ответа на user-вопрос. Ответ обуславливается на информацию из имеющегося графа знаний.

        :param query: User-вопрос на естественном языке.
        :type query: str
        :return: Кортеж из двух объектов: (1) cгенерированный ответ; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[str, ReturnInfo]
        """

        self.log("START QUESTION ANSWERING...", verbose=self.config.verbose)
        self.log(f"BASE_QUESTION ID: {create_id(query)}", verbose=self.config.verbose)
        self.log(f"BASE_QUESTION: {query}", verbose=self.config.verbose)

        answer = None
        self.log("STAGE#1 - KEY WORDS EXTRACTION", verbose=self.config.verbose)
        query_info, info = self.query_parser.extract_entities(query)
        self.log(f"RESULT:\n* EXTRACTED ENTITIES AMOUNT - {len(query_info.entities)}", verbose=self.config.verbose)

        if info.status == ReturnStatus.success:
            self.log("STAGE#2 - MATCHING KEY WORDS TO KG-NODES", verbose=self.config.verbose)
            info = self.knowledge_comparator.link_kgnodes_to_query(query_info)
            self.log(f"RESULT:\n* MATCHED KG-NODES AMOUNT - {len(query_info.linked_nodes)}",verbose=self.config.verbose)

        if info.status == ReturnStatus.success:
            self.log("STAGE#3 - RETRIEVING RELEVANT TRIPLETS FROM KG", verbose=self.config.verbose)
            retrieved_triplets, info = self.knowledge_retriever.retrieve(query_info)
            self.log(f"RESULT:\n* RETRIEVED TRIPLETS AMOUNT - {len(retrieved_triplets)}", verbose=self.config.verbose)

        if info.status == ReturnStatus.success:
            self.log("STAGE#4 - ANSWER GENERATION", verbose=self.config.verbose)
            answer, info = self.answer_generator.generate(query_info.query, retrieved_triplets)
            self.log(f"RESULT:\n* ANSWER - {answer}", verbose=self.config.verbose)

        self.log(f"STATUS: {STATUS_MESSAGE[info.status]}", verbose=self.config.verbose)

        return answer, info
