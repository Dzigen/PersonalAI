from dataclasses import dataclass, field
from typing import List, Tuple, Union, Dict

from .configs import KR_MAIN_LOG_PATH, AVAILABLE_TRIPLETS_FILTERS, AVAILABLE_TRIPLETS_RETRIEVERS
from .utils import BaseGraphSearchConfig, BaseTripletsFilterConfig, KnowledgeRetrieverStages
from .filtering_methods.TripletsFilter import TripletsFilterConfig
from .traversal_methods.BeamSearchTripletsRetriever import GraphBeamSearchConfig
from ......kg_model import KnowledgeGraphModel
from ......utils import Logger, ReturnStatus, ReturnInfo
from ......utils.errors import STATUS_MESSAGE
from ......utils.data_structs import create_id, QueryInfo, Triplet
from ......utils.cache_kv import CacheUtils
from ......db_drivers.kv_driver import KeyValueDriverConfig
from ......utils.cache_kv.CacheOperations import CacheOperations


@dataclass
class KnowledgeRetrieverConfig:
    """Конфигурация "Knowledge Retriever"-стадии.

    :param retriever_method: Наименование алгоритма для обхода вершин/рёбер графовой структуры данных (графа знаний) и извлечения релевантной информации. Значение по умолчанию 'astar'.
    :type retriever_method: str, optional
    :param retriever_config: Конфигурация выбранного алгоритма обхода графа. Значение по умолчанию AStarGraphSearchConfig().
    :type retriever_config: Union[BaseGraphSearchConfig, Dict], optional
    :param filter_method: Наименование алгоритма для фильтрации информации (триеплетов), извлечённой из графа знаний (в результате работы алгоритма обхода графа). Значение по умолчанию 'naive'.
    :type filter_method: str, optional
    :param filter_config: Конфигурация выбранного алгоритма фильтрации информации (триплетов). Значение по умолчанию TripletsFilterConfig().
    :type filter_config: Union[BaseTripletsFilterConfig, Dict], optional
    :param cache_table_name: Название таблицы в структуре (базе) данных, куда будут сохраняться (кешироваться) основные результаты работы KnowledgeRetriever-класса. Значение по умолчанию 'qa_kretriever_stage_cache'.
    :type cache_table_name: str, optional
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты. Значение по умолчанию Logger(KR_MAIN_LOG_PATH).
    :type log: Logger, optional
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool, optional
    """
    retriever_method: str = 'beamsearch'
    retriever_config: Union[BaseGraphSearchConfig, Dict] = field(default_factory=lambda: GraphBeamSearchConfig())
    filter_method: Union[None, str] = 'naive'
    filter_config: Union[BaseTripletsFilterConfig, Dict, None] = field(default_factory=lambda: TripletsFilterConfig())

    cache_table_name: Union[str, None] = 'qa_kretriever_stage_cache'
    log: Logger = field(default_factory=lambda: Logger(KR_MAIN_LOG_PATH))
    verbose: bool = False

    def to_str(self) -> str:
        str_r_config = [f"{k}:{v}" for k, v in self.retriever_config.items()] if isinstance(self.retriever_config, dict) else self.retriever_config.to_str()
        str_f_config = [f"{k}:{v}" for k, v in self.filter_config.items()] if isinstance(self.filter_config, dict) else (None if self.filter_config is None else self.filter_config.to_str())
        return f"{self.retriever_method};{str_r_config};{self.filter_method};{str_f_config}"


class KnowledgeRetriever(CacheUtils, CacheOperations):
    """Верхнеуровневый класс третьей стадии QA-конвейера для извлечения
    релевантной к user-вопросу информации из памяти (графа знаний) ассистента.

    :param kg_model: Модель памяти (графа знаний) ассистента. Значение по умолчанию 'astar'.
    :type kg_model: KnowledgeGraphModel
    :param config: Конфигурация 'Knowledge Retriever'-стадии. Значение по умолчанию KnowledgeRetrieverConfig().
    :type config: KnowledgeRetrieverConfig, optional
    :param cache_kvdriver_config: Конфигурация структуры данных для кеширования промежуточных результатов в рамках компонент данного класса. Значение по умолчению None.
    :type cache_kvdriver_config: Union[KeyValueDriverConfig, None], optional
    """

    def __init__(self, kg_model: KnowledgeGraphModel, config: KnowledgeRetrieverConfig = KnowledgeRetrieverConfig(),
                 cache_kvdriver_config: Union[None, KeyValueDriverConfig] = None) -> None:
        self.config = config
        self.kg_model = kg_model

        self.cachekv = self.init_cachekv(
            cache_kvdriver_config, config.cache_table_name)

        self.stages: KnowledgeRetrieverStages = KnowledgeRetrieverStages(
            triplets_retriever=AVAILABLE_TRIPLETS_RETRIEVERS[self.config.retriever_method]['class'](
                kg_model, config.log, self.config.retriever_config, cache_kvdriver_config, self.config.verbose),
        )

        if self.config.filter_method is not None:
            self.stages.triplets_filter = AVAILABLE_TRIPLETS_FILTERS[self.config.filter_method]['class'](
                kg_model, config.log, self.config.filter_config, cache_kvdriver_config, self.config.verbose)

        self.log = config.log
        self.verbose = config.verbose

    def validate_tripelts(self, triplets: List[Triplet]) -> List[Triplet]:
        self.log("Проверяем, что извлечённые триплеты являются валидными...",
                 verbose=self.config.verbose)
        self.log("Невалидные триплеты:", verbose=self.config.verbose)
        valid_triplets = []
        for triplet in triplets:
            # t_graph_exists = self.kg_model.graph_struct.db_conn.item_exist(triplet.id)
            r_graph_exists = self.kg_model.graph_struct.db_conn.item_exist(
                triplet.relation.id, id_type='relation')
            # sn_graph_exists = self.kg_model.graph_struct.db_conn.item_exist(triplet.start_node.id, id_type='node')
            # en_graph_exists = self.kg_model.graph_struct.db_conn.item_exist(triplet.end_node.id, id_type='node')

            r_vector_exists = self.kg_model.graph_embeddings.triplets_vcomposer.item_exist(
                triplet.relation.id)
            # sn_vector_exists = self.kg_model.graph_embeddings.nodes_vcomposers.item_exist(triplet.start_node.id)
            # en_vector_exists = self.kg_model.graph_embeddings.nodes_vcomposers.item_exist(triplet.end_node.id)

            if not (r_graph_exists and r_graph_exists):
                self.log(
                    f"* [graph - r:{r_graph_exists} | vector - r:{r_vector_exists}] {triplet}", verbose=self.config.verbose)
            else:
                valid_triplets.append(triplet)

        self.log(
            f"RESULT:\n* валидных - {len(valid_triplets)} \n* невалидных - {len(triplets) - len(valid_triplets)}", verbose=self.config.verbose)

        return valid_triplets

    def traverse_kg(self, query_info: QueryInfo) -> List[Triplet]:
        triplets = self.stages.triplets_retriever.get_relevant_triplets(query_info)
        self.log(f"RESULT: {len(triplets)}", verbose=self.config.verbose)
        for triplet in triplets:
            self.log(f"*[{triplet.id}] {triplet}", verbose=self.config.verbose)

        # косытль
        # triplets = self.validate_tripelts(triplets)

        return triplets

    def filter_triplets(self, query_info: QueryInfo, triplets: List[Triplet]) -> List[Triplet]:
        filtered_triplets = None
        if self.stages.triplets_filter is not None:
            filtered_triplets = self.stages.triplets_filter.apply_filter(query_info, triplets)
            self.log(f"RESULT: {len(filtered_triplets)}",
                     verbose=self.config.verbose)
            for triplet in filtered_triplets:
                self.log(f"*[{triplet.id}] {triplet}",
                         verbose=self.config.verbose)
        else:
            filtered_triplets = triplets
            self.log("Stage was omited!", verbose=self.config.verbose)

        return filtered_triplets

    def get_cache_key(self, query_info: QueryInfo) -> List[str]:
        str_tfilter_config = self.stages.triplets_filter.config.to_str() if self.stages.triplets_filter is not None else "None"
        return [self.config.retriever_method, self.stages.triplets_retriever.config.to_str(), str(self.config.filter_method),
                str_tfilter_config, query_info.to_str()]

    @CacheUtils.cache_method_output
    def retrieve(self, query_info: QueryInfo) -> Tuple[List[Triplet], ReturnInfo]:
        """Метод предназначен для извлечения релевантных к user-вопросу триплетов из графа знаний.

        :param query_info: Структура данных, которая хранит user-вопрос и связанную с ним информацию.
        :type query_info: QueryInfo
        :return: Кортеж из двух объектов: (1) список релевантных user-вопросу триплетов; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[List[Triplet], ReturnInfo]
        """
        self.log("START KNOWLEDGE RETRIEVING ...", verbose=self.config.verbose)
        self.log(
            f"BASE_QUESTION ID: {create_id(query_info.query)}", verbose=self.config.verbose)
        self.log(f"BASE_QUESTION: {query_info.query}",
                 verbose=self.config.verbose)

        rinfo = ReturnInfo()
        self.log("STAGE #3.1 - TRIPLETS EXTRACTION...",
                 verbose=self.config.verbose)
        triplets = self.traverse_kg(query_info)

        self.log("STAGE #3.2 - TRIPLETS FILTERING...", verbose=self.config.verbose)
        filtered_triplets = self.filter_triplets(query_info, triplets)

        if len(triplets) == 0:
            rinfo.status = ReturnStatus.zero_retrieved_triplets
            rinfo.message = STATUS_MESSAGE[rinfo.status]

        self.log(f"STATUS: {STATUS_MESSAGE[rinfo.status]}", verbose=self.config.verbose)

        return filtered_triplets, rinfo
