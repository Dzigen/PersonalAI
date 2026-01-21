from dataclasses import dataclass, field
from typing import List, Tuple, Union, Dict
from copy import deepcopy
from collections import Counter

from .configs import KR_MAIN_LOG_PATH, AVAILABLE_TRIPLETS_FILTERS, AVAILABLE_TRIPLETS_RETRIEVERS, \
    AVAILABLE_TFILTERS_CONFIGS, AVAILABLE_TRETRIEVERS_CONFIGS
from .utils import BaseGraphSearchConfig, BaseTripletsFilterConfig, KnowledgeRetrieverStages
from .filtering_methods.TripletsFilter import TripletsFilterConfig
from .traversal_methods.MixturedTripletsRetriever import MixturedGraphSearchConfig
from ......kg_model import KnowledgeGraphModel
from ......utils import Logger, ReturnStatus, ReturnInfo, accumulate_stage_info, \
    CompositeModuleDetailedResult, ModuleType, SimpleModuleResult
from ......utils.errors import STATUS_MESSAGE
from ......utils.data_structs import create_id, QueryInfo, Triplet, BaseComponentConfig
from ......utils.cache_kv import CacheUtils
from ......db_drivers.kv_driver import KeyValueDriverConfig
from ......utils.cache_kv.CacheOperations import CacheOperations


@dataclass
class KnowledgeRetrieverConfig(BaseComponentConfig):
    """Конфигурация "Knowledge Retriever"-стадии.

    :param retriever_method: Наименование алгоритма для обхода вершин/рёбер графовой структуры данных (графа знаний) и извлечения релевантной информации. Значение по умолчанию 'mixture'.
    :type retriever_method: str, optional
    :param retriever_config: Конфигурация выбранного алгоритма обхода графа. Значение по умолчанию MixturedGraphSearchConfig().
    :type retriever_config: Union[BaseGraphSearchConfig, Dict], optional
    :param filter_method: Наименование алгоритма для фильтрации информации (триеплетов), извлечённой из графа знаний (в результате работы алгоритма обхода графа). Значение по умолчанию 'naive'.
    :type filter_method: Union[str, None], optional
    :param filter_config: Конфигурация выбранного алгоритма фильтрации информации (триплетов). Значение по умолчанию TripletsFilterConfig().
    :type filter_config: Union[BaseTripletsFilterConfig, Dict, None], optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы KnowledgeRetriever-класса. Значение по умолчанию 'qa_kretriever_stage_cache'.
    :type cache_table_name: str, optional
    """
    retriever_method: str = 'mixture'
    retriever_config: Union[Dict, BaseGraphSearchConfig] = field(default_factory=lambda: MixturedGraphSearchConfig())
    filter_method: Union[None, str] = 'naive'
    filter_config: Union[BaseTripletsFilterConfig, Dict, None] = field(default_factory=lambda: TripletsFilterConfig())

    cache_table_name: Union[str, None] = 'qa_kretriever_stage_cache'
    log: Logger = field(default_factory=lambda: Logger(KR_MAIN_LOG_PATH))

    def to_str(self) -> str:
        str_r_config = [f"{k}:{v}" for k, v in self.retriever_config.items()] if isinstance(self.retriever_config, dict) else self.retriever_config.to_str()
        str_f_config = [f"{k}:{v}" for k, v in self.filter_config.items()] if isinstance(self.filter_config, dict) else (None if self.filter_config is None else self.filter_config.to_str())
        return f"{self.retriever_method};{str_r_config};{self.filter_method};{str_f_config}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = KnowledgeRetrieverConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.retriever_config, dict):
            self.retriever_config = AVAILABLE_TRETRIEVERS_CONFIGS[self.retriever_method].from_dict(self.retriever_config)
        else:
            self.retriever_config.formate_fields()

        if isinstance(self.filter_config, dict):
            self.filter_config = AVAILABLE_TFILTERS_CONFIGS[self.filter_method].from_dict(self.filter_config)
        elif self.filter_config is not None:
            self.filter_config.formate_fields()


class KnowledgeRetriever(CacheUtils, CacheOperations):
    """Верхнеуровневый класс третьей стадии QA-конвейера для извлечения
    релевантной к user-вопросу информации из памяти (графа знаний) ассистента.

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param config: Конфигурация 'Knowledge Retriever'-стадии. Значение по умолчанию KnowledgeRetrieverConfig().
    :type config: Union[KnowledgeRetrieverConfig,Dict], optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчанию None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    """

    def __init__(self, kg_model: KnowledgeGraphModel, config: Union[KnowledgeRetrieverConfig, Dict] = KnowledgeRetrieverConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None) -> None:
        if isinstance(config, dict):
            config: KnowledgeRetrieverConfig = KnowledgeRetrieverConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config = config

        self.kg_model = kg_model

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, config.cache_table_name)

        self.stages: KnowledgeRetrieverStages = KnowledgeRetrieverStages(
            triplets_retriever=AVAILABLE_TRIPLETS_RETRIEVERS[self.config.retriever_method](
                kg_model, config.log, self.config.retriever_config, cache_kvdriver_config, self.config.verbose),
        )

        if self.config.filter_method is not None:
            self.stages.triplets_filter = AVAILABLE_TRIPLETS_FILTERS[self.config.filter_method](
                kg_model, config.log, self.config.filter_config, cache_kvdriver_config, self.config.verbose)

        self.log = config.log
        self.verbose = config.verbose

    def validate_tripelts(self, triplets: List[Triplet]) -> List[Triplet]:
        self.log("Проверяем, что извлечённые триплеты являются валидными...",
                 verbose=self.verbose)
        self.log("Невалидные триплеты:", verbose=self.verbose)
        valid_triplets = []
        for triplet in triplets:
            r_graph_exists = self.kg_model.graph_struct.db_conn.item_exist(
                triplet.relation.get_info(), id_type='relation')
            r_vector_exists = self.kg_model.graph_embeddings.triplets_vcomposer.item_exist(
                triplet.relation.id)

            if not (r_graph_exists and r_graph_exists):
                self.log(
                    f"* [graph - r:{r_graph_exists} | vector - r:{r_vector_exists}] {triplet}", verbose=self.verbose)
            else:
                valid_triplets.append(triplet)

        self.log(
            f"RESULT:\n* валидных - {len(valid_triplets)} \n* невалидных - {len(triplets) - len(valid_triplets)}", verbose=self.verbose)

        return valid_triplets

    def traverse_kg(self, query_info: QueryInfo) -> Tuple[List[Triplet], SimpleModuleResult]:
        """Метод реализует извлечение релевантных триплетов из графа знаний.

        :param query_info: Структура с user-вопросом и дополнительными полями.
        :type query_info: QueryInfo
        :return: Кортеж из двух объектов: (1) cписок извлечённых триплетов; (2) структура данных с промежуточными результатами реботы метода.
        :rtype: Tuple[List[Triplet], SimpleModuleResult]
        """
        triplets, trace = self.stages.triplets_retriever.get_relevant_triplets(query_info)
        self.log(f"RESULT: {len(triplets)}", verbose=self.verbose)
        for triplet in triplets:
            self.log(f"*[{triplet.id}] {triplet}", verbose=self.verbose)

        # костыль
        # triplets = self.validate_tripelts(triplets)

        return triplets, trace

    def filter_triplets(self, query_info: QueryInfo, triplets: List[Triplet]) -> Tuple[List[Triplet], SimpleModuleResult]:
        """Метод фильтрует/ранжирует триплеты, извлечённые из графа.

        :param query_info: Структура с user-вопросом и дополнительными полями.
        :type query_info: QueryInfo
        :param triplets: Список триплетов, подлежащих фильтрации/ранжированию.
        :type triplets: List[Triplet]
        :return: Кортеж из двух объектов: (1) отфильтрованный/ранжированный список триплетов; (2) структура данных с промежуточными результатами реботы метода.
        :rtype: Tuple[List[Triplet], SimpleModuleResult]
        """
        filtered_triplets = None
        if self.stages.triplets_filter is not None:
            filtered_triplets, trace = self.stages.triplets_filter.apply_filter(query_info, triplets)
            self.log(f"RESULT: {len(filtered_triplets)}",
                     verbose=self.verbose)
            for triplet in filtered_triplets:
                self.log(f"*[{triplet.id}] {triplet}",
                         verbose=self.verbose)
        else:
            filtered_triplets = triplets
            self.log("Stage was omited!", verbose=self.verbose)

        return filtered_triplets, trace

    def get_cache_key(self, query_info: QueryInfo) -> List[str]:
        """Формирует ключ кэша для для результатов извлечения/фильтрации.

        В ключ включается метод и конфигурация извлечения триплетов, метод и конфигурацию фильтра, сериализованное представление входного QueryInfo.

        :param query_info: Структура с исходным запросом и дополнительными полями.
        :type query_info: QueryInfo
        :return: Список строк, используемый как составной ключ кеша.
        :rtype: List[str]
        """
        str_tfilter_config = self.stages.triplets_filter.config.to_str() if self.stages.triplets_filter is not None else "None"
        return [self.config.retriever_method, self.stages.triplets_retriever.config.to_str(), str(self.config.filter_method),
                str_tfilter_config, query_info.to_str()]

    @accumulate_stage_info
    @CacheUtils.cache_method_output
    def retrieve(self, query_info: QueryInfo) -> Tuple[List[Triplet], ReturnInfo, CompositeModuleDetailedResult]:
        """Метод предназначен для извлечения релевантных к user-вопросу триплетов из графа знаний.

        :param query_info: Структура данных, которая хранит user-вопрос и связанную с ним информацию.
        :type query_info: QueryInfo
        :return: Кортеж из трёх объектов: (1) список релевантных user-вопросу триплетов; (2) статус завершения операции с пояснительной информацией; (3) структура данных с промежуточными результатами реботы метода.
        :rtype: Tuple[List[Triplet], ReturnInfo, CompositeModuleDetailedResult]
        """
        self.log("START KNOWLEDGE RETRIEVING ...", verbose=self.verbose)
        self.log(f"BASE_QUESTION ID: {create_id(query_info.query)}", verbose=self.verbose)
        self.log(f"BASE_QUESTION: {query_info.query}", verbose=self.verbose)

        rinfo, module_trace = ReturnInfo(), CompositeModuleDetailedResult()
        self.log("STAGE #3.1 - TRIPLETS EXTRACTION...", verbose=self.verbose)
        triplets, trace = self.traverse_kg(query_info)
        module_trace.add("traverse_kg", ModuleType.step, trace)

        triplet_types_freq = dict(Counter([triplet.relation.type.value for triplet in triplets]))
        self.log(f"Респределение количества типов триплетов: {triplet_types_freq}", verbose=self.verbose)

        self.log("STAGE #3.2 - TRIPLETS FILTERING...", verbose=self.verbose)
        filtered_triplets, trace = self.filter_triplets(query_info, triplets)
        module_trace.add("filter_triplets", ModuleType.step, trace)

        triplet_types_freq = dict(Counter([triplet.relation.type.value for triplet in filtered_triplets]))
        self.log(f"Респределение количества типов триплетов: {triplet_types_freq}", verbose=self.verbose)

        if len(triplets) == 0:
            rinfo.status = ReturnStatus.zero_retrieved_triplets
            rinfo.message = STATUS_MESSAGE[rinfo.status]

        self.log(f"STATUS: {STATUS_MESSAGE[rinfo.status]}", verbose=self.verbose)

        return filtered_triplets, rinfo, module_trace
