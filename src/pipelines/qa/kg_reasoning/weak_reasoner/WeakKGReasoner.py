from dataclasses import dataclass, field
from typing import Tuple, Union, List, Dict
from copy import deepcopy

from .config import WKGR_MAIN_LOG_PATH
from .utils import WeakKGReasonerStages
from .query_parser import QueryLLMParser, QueryLLMParserConfig
from .knowledge_comparator import KnowledgeComparator, KnowledgeComparatorConfig
from .knowledge_retriever import KnowledgeRetriever, KnowledgeRetrieverConfig
from .answer_generator import QALLMGenerator, QALLMGeneratorConfig
from ..utils import AbstractKGReasoner, BaseKGReasonerConfig
from .....utils.data_structs import create_id, QueryInfo, Triplet, BaseComponentConfig, LanguageConfig
from .....utils import Logger, ReturnInfo, ReturnStatus, update_rinfo
from .....utils.cache_kv import CacheUtils
from .....kg_model import KnowledgeGraphModel
from .....db_drivers.kv_driver import KeyValueDriverConfig
from .....utils.agent_stat_analyzer import AgentStatAnalyzerConfig


@dataclass
class WeakKGReasonerConfig(BaseKGReasonerConfig, BaseComponentConfig, LanguageConfig):
    """Конфигурация weak-версии пайплайна по ризонингу на графе знаний.

    :param query_parser_config: Конфигурация первой стадии reasoner-конвейера: извлечение сущностей из user-вопроса. Значение по умолчанию QueryLLMParserConfig().
    :type query_parser_config: Union[None,Dict,QueryLLMParserConfig], optional
    :param knowledge_comparator_config: Конфигурация второй стадии reasoner-конвейера: сопоставление (match) сущностей из user-вопроса с информацией в графе знаний. Значение по умолчанию KnowledgeComparatorConfig().
    :type knowledge_comparator_config: Union[None,Dict,KnowledgeComparatorConfig], optional
    :param knowledge_retriever_config: Конфигурация третьей стадии reasoner-конвейера: извлечение релевантной информации из графа знаний для user-вопроса. Значение по умолчанию KnowledgeRetrieverConfig().
    :type knowledge_retriever_config: Union[Dict,KnowledgeRetrieverConfig], optional
    :param answer_generator_config: Конфигурация четвёртой стадии reasoner-конвейера: условная генерация ответа на user-вопрос. Значение по умолчанию QALLMGeneratorConfig().
    :type answer_generator_config: Union[Dict,QALLMGeneratorConfig], optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы WeakKGReasoner-класса. Значение по умолчанию 'qa_weakreasoner_cache'.
    :type cache_table_name: str, optional
    """
    query_parser_config: Union[None, Dict, QueryLLMParserConfig] = field(
        default_factory=lambda: QueryLLMParserConfig())
    knowledge_comparator_config: Union[None, Dict, KnowledgeComparatorConfig] = field(
        default_factory=lambda: KnowledgeComparatorConfig())
    knowledge_retriever_config: Union[Dict, KnowledgeRetrieverConfig] = field(
        default_factory=lambda: KnowledgeRetrieverConfig())
    answer_generator_config: Union[Dict, QALLMGeneratorConfig] = field(
        default_factory=lambda: QALLMGeneratorConfig())

    cache_table_name: str = 'qa_weakreasoner_cache'
    log: Logger = field(default_factory=lambda: Logger(WKGR_MAIN_LOG_PATH))

    def to_str(self) -> str:
        str_qparser_config = self.query_parser_config.to_str() if self.query_parser_config is not None else "None"
        str_kcomp_config = self.knowledge_comparator_config.to_str() if self.knowledge_comparator_config is not None else "None"
        str_kretr_config = self.knowledge_retriever_config.to_str()
        str_answgen_config = self.answer_generator_config.to_str()
        return f"{str_qparser_config};{str_kcomp_config};{str_kretr_config};{str_answgen_config}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = WeakKGReasonerConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.query_parser_config, dict):
            self.query_parser_config = QueryLLMParserConfig.from_dict(self.query_parser_config)
        elif self.query_parser_config is not None:
            self.query_parser_config.formate_fields()

        if isinstance(self.knowledge_comparator_config, dict):
            self.knowledge_comparator_config = KnowledgeComparatorConfig.from_dict(self.knowledge_comparator_config)
        elif self.knowledge_comparator_config is not None:
            self.knowledge_comparator_config.formate_fields()

        if isinstance(self.knowledge_retriever_config, dict):
            self.knowledge_retriever_config = KnowledgeRetrieverConfig.from_dict(self.knowledge_retriever_config)
        else:
            self.knowledge_retriever_config.formate_fields()

        if isinstance(self.answer_generator_config, dict):
            self.answer_generator_config = QALLMGeneratorConfig.from_dict(self.answer_generator_config)
        else:
            self.answer_generator_config.formate_fields()


class WeakKGReasoner(AbstractKGReasoner, CacheUtils):
    """Weak-версия пайплайна по ризонигу на графе знаний с целью извлечения релевантной информации к запросу.

    :param agent: Коннектор к конкретному LLM-агенту для выполнения inference-операций.
    :type agent: AbstractAgentConnector
    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param config: Конфигурация WeakKGReasoner-пайплайна. Значение по умолчанию WeakKGReasonerConfig().
    :type config: Union[WeakKGReasonerConfig,Dict], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    :param inferencestat_config: Конфигурация компоненты для сбора информации и расчёта статистик по результатам выполнения inference-операциий в рамках LLM-задач. Значение по умолчанию None.
    :type inferencestat_config: Union[None, AgentStatAnalyzerConfig], optional
    """

    def __init__(self, kg_model: KnowledgeGraphModel, config: Union[WeakKGReasonerConfig, Dict] = WeakKGReasonerConfig(),
                 cache_kvdriver_config: Union[KeyValueDriverConfig, None] = None,
                 inferencestat_config: Union[None, AgentStatAnalyzerConfig] = None):
        if isinstance(config, dict):
            config: WeakKGReasonerConfig = WeakKGReasonerConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config = config

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, config.cache_table_name)

        agent = kg_model.AVAILABLE_AGENTS[kg_model.AGENTS_MAP.qa_pipeline]
        self.using_agent_info = {'kw': agent.CONNECTOR_KW, 'config': agent.config}

        self.stages: WeakKGReasonerStages = WeakKGReasonerStages(
            knowledge_retriever=KnowledgeRetriever(
                kg_model, self.config.knowledge_retriever_config, cache_kvdriver_config),
            answer_generator=QALLMGenerator(
                agent, self.config.answer_generator_config, cache_kvdriver_config, inferencestat_config)
        )

        if self.config.query_parser_config is not None:
            self.stages.query_parser = QueryLLMParser(
                agent, self.config.query_parser_config,
                cache_kvdriver_config, inferencestat_config)
            self.stages.knowledge_comparator = KnowledgeComparator(
                kg_model, self.config.knowledge_comparator_config,
                cache_kvdriver_config)

        self.log = config.log
        self.verbose = config.verbose

    def extract_entities(self, query_info: QueryInfo) -> Tuple[Union[None, List[str]], ReturnInfo]:
        entities, rinfo = None, ReturnInfo()

        if self.stages.query_parser is None:
            self.log("Stage #1 was omited!", verbose=self.verbose)
        else:
            entities, rinfo = self.stages.query_parser.extract_entities(query_info)
            if rinfo.status != ReturnStatus.success:
                self.log("Operation ended with error!", verbose=self.verbose)
            else:
                self.log("Operation ended successfully", verbose=self.verbose)
                self.log(f"RESULT:\n* EXTRACTED ENTITIES AMOUNT - {len(entities)}\n* EXTRACTED ENTITIES - {entities}", verbose=self.verbose)

        return entities, rinfo

    def match_entities_to_kgnodes(self, query_info: QueryInfo) -> Tuple[Union[None, List[object]], Union[None, List[object]], ReturnInfo]:
        linked_nodes, linked_nodes_by_entities, rinfo = None, None, ReturnInfo()
        if self.stages.query_parser is None:
            self.log("Stage #2 was omited!", verbose=self.verbose)
        else:
            linked_nodes, linked_nodes_by_entities, rinfo = self.stages.knowledge_comparator.link_kgnodes_to_query(
                query_info)
            if rinfo.status != ReturnStatus.success:
                self.log("Operation ended with error!", verbose=self.verbose)
            else:
                self.log("Operation ended successfully", verbose=self.verbose)
                self.log(f"RESULT: {len(linked_nodes)}", verbose=self.verbose)
                for node in linked_nodes:
                    self.log(f"*[{node.id}] {node.text}", verbose=self.verbose)

        return linked_nodes, linked_nodes_by_entities, rinfo

    def traverse_knowledge_graph(self, query_info: QueryInfo) -> Tuple[Union[None, List[Triplet]], ReturnInfo]:
        retrieved_triplets, rinfo = self.stages.knowledge_retriever.retrieve(query_info)
        if rinfo.status != ReturnStatus.success:
            self.log("Operation ended with error!", verbose=self.verbose)
        else:
            self.log("Operation ended successfully", verbose=self.verbose)
            self.log(f"RESULT: {len(retrieved_triplets)}", verbose=self.verbose)
            for triplet in retrieved_triplets:
                self.log(f"* {triplet}", verbose=self.verbose)

        return retrieved_triplets, rinfo

    def generate_answer(self, query_info: QueryInfo, retrieved_triplets: List[Triplet]) -> Tuple[Union[None, str], ReturnInfo]:
        answer, rinfo = self.stages.answer_generator.generate(query_info.query, retrieved_triplets)
        if rinfo.status != ReturnStatus.success:
            self.log("Operation ended with error!", verbose=self.verbose)
        else:
            self.log("Operation ended successfully", verbose=self.verbose)
            self.log(f"RESULT:\n* ANSWER - {answer}", verbose=self.verbose)

        return answer, rinfo

    def get_cache_key(self, query: str) -> List[str]:
        str_using_agent_config = f"{self.using_agent_info['kw']}:{self.using_agent_info['config'].to_str()}"
        return [self.config.to_str(), str_using_agent_config, query]

    @CacheUtils.cache_method_output
    def perform(self, query: str) -> Tuple[str, ReturnInfo]:
        """Метод предназначен для выполнения ризонинга на графе знаний с помощью указанного запроса с целью извлечения релевантной информации.

        :param query: запрос на естественном языке.
        :type query: str
        :return: Кортеж из двух объектов: (1) извлечённая/релевантная информация/ответа на запрос; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[str, ReturnInfo]
        """
        self.log("START WEAK KG-REASONING...", verbose=self.verbose)
        self.log(f"BASE_QUESTION ID: {create_id(query)}", verbose=self.verbose)
        self.log(f"BASE_QUESTION: {query}", verbose=self.verbose)

        answer, rinfo = None, ReturnInfo()
        query_info = QueryInfo(query=query)

        self.log("STAGE#1 - KEY WORDS EXTRACTION", verbose=self.verbose)
        query_info.entities, ee_rinfo = self.extract_entities(query_info)
        update_rinfo(rinfo, ee_rinfo)

        self.log("STAGE#2 - MATCHING KEY WORDS TO KG-NODES", verbose=self.verbose)
        if rinfo.status == ReturnStatus.success:
            query_info.linked_nodes, query_info.linked_nodes_by_entities, me_rinfo = \
                self.match_entities_to_kgnodes(query_info)
            update_rinfo(rinfo, me_rinfo)
        else:
            self.log("During previous steps error occurs.", verbose=self.verbose)

        self.log("STAGE#3 - RETRIEVING RELEVANT TRIPLETS FROM KG", verbose=self.verbose)
        if rinfo.status == ReturnStatus.success:
            retrieved_triplets, tkg_rinfo = self.traverse_knowledge_graph(query_info)
            update_rinfo(rinfo, tkg_rinfo)
        else:
            self.log("During previous steps error occurs.", verbose=self.verbose)

        self.log("STAGE#4 - ANSWER GENERATION", verbose=self.verbose)
        if rinfo.status == ReturnStatus.success:
            answer, ag_rinfo = self.generate_answer(query_info, retrieved_triplets)
            update_rinfo(rinfo, ag_rinfo)
        else:
            self.log("During previous steps error occurs.", verbose=self.verbose)

        self.log(f"STATUS: {rinfo.status}", verbose=self.verbose)

        return answer, rinfo
