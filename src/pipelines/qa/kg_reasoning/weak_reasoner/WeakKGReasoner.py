from dataclasses import dataclass, field
from typing import Tuple, Union, List

from .config import WKGR_MAIN_LOG_PATH
from .query_parser import QueryLLMParser, QueryLLMParserConfig
from .knowledge_comparator import KnowledgeComparator, KnowledgeComparatorConfig
from .knowledge_retriever import KnowledgeRetriever, KnowledgeRetrieverConfig
from .answer_generator import QALLMGenerator, QALLMGeneratorConfig
from ..utils import AbstractKGReasoner, BaseKGReasonerConfig
from .....utils.data_structs import create_id, QueryInfo, Triplet
from .....utils import Logger, ReturnInfo, ReturnStatus, update_rinfo
from .....utils.cache_kv import CacheUtils
from .....kg_model import KnowledgeGraphModel
from .....db_drivers.kv_driver import KeyValueDriverConfig

@dataclass
class WeakKGReasonerConfig(BaseKGReasonerConfig):
    """Конфигурация weak-версии пайплайна по ризонингу на графе знаний.

    :param query_parser_config: Конфигурация первой стадии reasoner-конвейера: извлечение сущностей из user-вопроса. Значение по умолчанию QueryLLMParserConfig().
    :type query_parser_config: Union[None,QueryLLMParserConfig], optional
    :param knowledge_comparator_config: Конфигурация второй стадии reasoner-конвейера: сопоставление (match) сущностей из user-вопроса с информацией в графе знаний. Значение по умолчанию KnowledgeComparatorConfig().
    :type knowledge_comparator_config: Union[None,KnowledgeComparatorConfig], optional
    :param knowledge_retriever_config: Конфигурация третьей стадии reasoner-конвейера: извлечение релевантной информации из графа знаний для user-вопроса. Значение по умолчанию KnowledgeRetrieverConfig().
    :type knowledge_retriever_config: KnowledgeRetrieverConfig, optional
    :param answer_generator_config: Конфигурация четвёртой стадии reasoner-конвейера: условная генерация ответа на user-вопрос. Значение по умолчанию QALLMGeneratorConfig().
    :type answer_generator_config: QALLMGeneratorConfig, optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы WeakKGReasoner-класса. Значение по умолчанию 'qa_weakreasoner_cache'.
    :type cache_table_name: str, optional
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты. Значение по умолчанию Logger(WKGR_MAIN_LOG_PATH).
    :type log: Logger, optional
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool, optional
    """
    query_parser_config: Union[None,QueryLLMParserConfig] = field(default_factory=lambda: QueryLLMParserConfig())
    knowledge_comparator_config: Union[None,KnowledgeComparatorConfig] = field(default_factory=lambda: KnowledgeComparatorConfig())
    knowledge_retriever_config: KnowledgeRetrieverConfig = field(default_factory=lambda: KnowledgeRetrieverConfig())
    answer_generator_config: QALLMGeneratorConfig = field(default_factory=lambda: QALLMGeneratorConfig())

    cache_table_name: str = 'qa_weakreasoner_cache'
    log: Logger = field(default_factory=lambda: Logger(WKGR_MAIN_LOG_PATH))
    verbose: bool = False

    def to_str(self) -> str:
        str_qparser_config = self.query_parser_config.to_str() if self.query_parser_config is not None else "None"
        str_kcomp_config = self.knowledge_comparator_config.to_str() if self.knowledge_comparator_config is not None else "None"
        str_kretr_config = self.knowledge_retriever_config.to_str()
        str_answgen_config = self.answer_generator_config.to_str()
        return f"{str_qparser_config};{str_kcomp_config};{str_kretr_config};{str_answgen_config}"

class WeakKGReasoner(AbstractKGReasoner, CacheUtils):
    """Weak-версия пайплайна по ризонигу на графе знаний с целью извлечения релевантной информации к запросу.

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param config: Конфигурация WeakKGReasoner-пайплайна. Значение по умолчанию WeakKGReasonerConfig().
    :type config: WeakKGReasonerConfig, optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    """

    def __init__(self, kg_model: KnowledgeGraphModel, config: WeakKGReasonerConfig = WeakKGReasonerConfig(),
                 cache_kvdriver_config: Union[KeyValueDriverConfig, None] = None):
        self.config = config

        self.cachekv = self.init_cachekv(cache_kvdriver_config, config.cache_table_name)

        if self.config.query_parser_config is None:
            self.query_parser = None
            self.knowledge_comparator = None
        else:
            self.query_parser = QueryLLMParser(
                self.config.query_parser_config, cache_kvdriver_config)
            self.knowledge_comparator = KnowledgeComparator(
                kg_model, self.config.knowledge_comparator_config, cache_kvdriver_config)

        self.knowledge_retriever = KnowledgeRetriever(
            kg_model, self.config.knowledge_retriever_config, cache_kvdriver_config)
        self.answer_generator = QALLMGenerator(
            self.config.answer_generator_config, cache_kvdriver_config)

        self.log = config.log
        self.verbose = config.verbose

    def clear_kv_caches(self, level: str = 'all') -> None:
        if type(level) is not str:
            raise TypeError(f"Аргумент переменной 'level' должен иметь тип 'str'; сейчас аргумент имеет тип '{type(level)}'")
        if level not in ['all', 'current', 'other']:
            raise ValueError(f"Аргумент переменной 'level' должен принимать одно из трёх значенией: 'all', 'current' или 'other'. Полученное значение: '{level}'")

        if level in ['current', 'all']:
            self.cachekv.clear()

        if level in ['other', 'all']:
            if self.query_parser is not None:
                self.query_parser.clear_kv_caches(level='all')
            if self.knowledge_comparator is not None:
                self.knowledge_comparator.clear_kv_caches(level='all')

            self.knowledge_retriever.clear_kv_caches(level='all')
            self.answer_generator.clear_kv_caches(level='all')

    def extract_entities(self, query_info: QueryInfo) -> Tuple[Union[None, List[str]], ReturnInfo]:
        entities, rinfo = None, ReturnInfo()

        if self.query_parser is None:
            self.log("Stage #1 was omited!", verbose=self.config.verbose)
        else:
            entities, rinfo = self.query_parser.extract_entities(query_info)
            if rinfo.status != ReturnStatus.success:
                self.log("Operation ended with error!", verbose=self.verbose)
            else:
                self.log("Operation ended successfully", verbose=self.verbose)
                self.log(f"RESULT:\n* EXTRACTED ENTITIES AMOUNT - {len(entities)}\n* EXTRACTED ENTITIES - {entities}", verbose=self.config.verbose)

        return entities, rinfo

    def match_entities_to_kgnodes(self, query_info: QueryInfo) -> Tuple[Union[None, List[object]], Union[None, List[object]], ReturnInfo]:
        linked_nodes, linked_nodes_by_entities, rinfo = None, None, ReturnInfo()
        if self.query_parser is None:
            self.log("Stage #2 was omited!", verbose=self.config.verbose)
        else:
            linked_nodes, linked_nodes_by_entities, rinfo = self.knowledge_comparator.link_kgnodes_to_query(query_info)
            if rinfo.status != ReturnStatus.success:
                self.log("Operation ended with error!", verbose=self.verbose)
            else:
                self.log("Operation ended successfully", verbose=self.verbose)
                self.log(f"RESULT: {len(query_info.linked_nodes)}", verbose=self.config.verbose)
                for node in query_info.linked_nodes:
                    self.log(f"*[{node.id}] {node.document}", verbose=self.config.verbose)

        return linked_nodes, linked_nodes_by_entities, rinfo

    def traverse_knowledge_graph(self, query_info: QueryInfo) -> Tuple[Union[None,List[Triplet]], ReturnInfo]:
        retrieved_triplets, rinfo = self.knowledge_retriever.retrieve(query_info)
        if rinfo.status != ReturnStatus.success:
            self.log("Operation ended with error!", verbose=self.verbose)
        else:
            self.log("Operation ended successfully", verbose=self.verbose)
            self.log(f"RESULT: {len(retrieved_triplets)}", verbose=self.config.verbose)
            for triplet in retrieved_triplets:
                self.log(f"* {triplet}", verbose=self.config.verbose)

        return retrieved_triplets, rinfo

    def generate_answer(self, query_info: QueryInfo, retrieved_triplets: List[Triplet]) -> Tuple[Union[None,str], ReturnInfo]:
        answer, rinfo = self.answer_generator.generate(query_info.query, retrieved_triplets)
        if rinfo.status != ReturnStatus.success:
            self.log("Operation ended with error!", verbose=self.verbose)
        else:
            self.log("Operation ended successfully", verbose=self.verbose)
            self.log(f"RESULT:\n* ANSWER - {answer}", verbose=self.config.verbose)

        return answer, rinfo

    def get_cache_key(self, query: str) -> List[str]:
        return [self.config.to_str(), query]

    @CacheUtils.cache_method_output
    def perform(self, query: str) -> Tuple[str, ReturnInfo]:
        """Метод предназначен для выполнения ризонинга на графе знаний с помощью указанного запроса с целью извлечения релевантной информации.

        :param query: запрос на естественном языке.
        :type query: str
        :return: Кортеж из двух объектов: (1) извлечённая/релевантная информация/ответа на запрос; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[str, ReturnInfo]
        """
        self.log("START WEAK KG-REASONING...", verbose=self.config.verbose)
        self.log(f"BASE_QUESTION ID: {create_id(query)}", verbose=self.config.verbose)
        self.log(f"BASE_QUESTION: {query}", verbose=self.config.verbose)

        answer, rinfo = None, ReturnInfo()
        query_info = QueryInfo(query=query)

        self.log("STAGE#1 - KEY WORDS EXTRACTION", verbose=self.config.verbose)
        query_info.entities, ee_rinfo = self.extract_entities(self, query_info)
        update_rinfo(rinfo, ee_rinfo)


        self.log("STAGE#2 - MATCHING KEY WORDS TO KG-NODES", verbose=self.config.verbose)
        if rinfo.status == ReturnStatus.success:
            query_info.linked_nodes, query_info.linked_nodes_by_entities, me_rinfo = self.match_entities_to_kgnodes(query_info)
            update_rinfo(rinfo, me_rinfo)
        else:
            self.log("During previous steps error occurs.", verbose=self.verbose)

        self.log("STAGE#3 - RETRIEVING RELEVANT TRIPLETS FROM KG", verbose=self.config.verbose)
        if rinfo.status == ReturnStatus.success:
            retrieved_triplets, tkg_rinfo = self.traverse_knowledge_graph(query_info)
            update_rinfo(rinfo, tkg_rinfo)
        else:
            self.log("During previous steps error occurs.", verbose=self.verbose)

        self.log("STAGE#4 - ANSWER GENERATION", verbose=self.config.verbose)
        if rinfo.status == ReturnStatus.success:
            answer, ag_rinfo = self.answer_generator(query_info, retrieved_triplets)
            update_rinfo(rinfo, ag_rinfo)
        else:
            self.log("During previous steps error occurs.", verbose=self.verbose)

        self.log(f"STATUS: {rinfo.status}", verbose=self.config.verbose)

        return answer, rinfo
