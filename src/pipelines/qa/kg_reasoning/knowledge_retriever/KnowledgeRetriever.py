from dataclasses import dataclass, field
from typing import List, Tuple

from .configs import KR_MAIN_LOG_PATH, AVAILABLE_TRIPLETS_FILTERS, AVAILABLE_TRIPLETS_RETRIEVERS
from .utils import BaseGraphSearchConfig, BaseTripletsFilterConfig
from .TripletsFilter import TripletsFilterConfig
from .AStarTripletsRetriever import AStarGraphSearchConfig

from ....utils.data_structs import QueryInfo, Triplet
from ....kg_model import KnowledgeGraphModel
from ....utils import Logger, ReturnStatus, ReturnInfo
from ....utils.errors import STATUS_MESSAGE
from ....utils.data_structs import create_id

@dataclass
class KnowledgeRetrieverConfig:
    """Конфигурация "Knowledge Retriever"-стадии.

    :param retriever_method: Значение по умолчанию 'astar'.
    :type retriever_method: str
    :param retriever_config: Значение по умолчанию AStarGraphSearchConfig().
    :type retriever_config: BaseGraphSearchConfig
    :param filter_method: Значение по умолчанию 'naive'.
    :type filter_method: str
    :param filter_config: Значение по умолчанию TripletsFilterConfig().
    :type filter_config: BaseTripletsFilterConfig
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты. Значение по умолчанию Logger(RETRIEVER_LOG_PATH).
    :type log: Logger
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool
    """
    retriever_method: str = 'astar'
    retriever_config: BaseGraphSearchConfig = field(default_factory=lambda: AStarGraphSearchConfig())
    filter_method: str = 'naive'
    filter_config: BaseTripletsFilterConfig = field(default_factory=lambda: TripletsFilterConfig())
    log: Logger = field(default_factory=lambda: Logger(KR_MAIN_LOG_PATH))
    verbose: bool = False

class KnowledgeRetriever:
    """Верхнеуровневый класс третьей стадии QA-конвейера для извлечения
    релевантной к user-вопросу информации из памяти (графа знаний) ассистента.

    :param kg_model: Модель памяти (графа знаний) ассистента. Значение по умолчанию 'astar'.
    :type kg_model: KnowledgeGraphModel
    :param config: Конфигурация 'Knowledge Retriever'-стадии. Значение по умолчанию KnowledgeRetrieverConfig().
    :type config: KnowledgeRetrieverConfig
    """
    def __init__(self, kg_model: KnowledgeGraphModel, config: KnowledgeRetrieverConfig = KnowledgeRetrieverConfig()) -> None:
        self.config = config
        self.kg_model = kg_model
        self.log = config.log

        self.graph_retriever = AVAILABLE_TRIPLETS_RETRIEVERS[self.config.retriever_method](
            kg_model, self.log, self.config.retriever_config, self.config.verbose)

        self.triplets_filter = AVAILABLE_TRIPLETS_FILTERS[self.config.filter_method](
            kg_model, self.log, self.config.filter_config, self.config.verbose)

    def retrieve(self, query_info: QueryInfo) -> Tuple[List[Triplet], ReturnInfo]:
        """Метод предназначен для извлечения релевантных к user-вопросу триплетов из графа знаний.

        :param query_info: Структура данных, которая хранит user-вопрос и связанную с ним информацию.
        :type query_info: QueryInfo
        :return: Кортеж из двух объектов: (1) список релевантных user-вопросу триплетов; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[List[Triplet], ReturnInfo]
        """
        self.log("START KNOWLEDGE RETRIEVING ...", verbose=self.config.verbose)
        self.log(f"BASE_QUESTION ID: {create_id(query_info.query)}", verbose=self.config.verbose)
        self.log(f"BASE_QUESTION: {query_info.query}", verbose=self.config.verbose)

        info = ReturnInfo()
        self.log("STAGE #3.1 - TRIPLETS EXTRACTION...", verbose=self.config.verbose)
        triplets = self.graph_retriever.get_relevant_triplets(query_info)
        self.log(f"RESULT: {len(triplets)}", verbose=self.config.verbose)
        for triplet in triplets:
            self.log(f"*[{triplet.id}] {triplet}", verbose=self.config.verbose)

        # костыль
        # self.log("Проверяем, что извлечённый триплеты являются валидными...", verbose=self.config.verbose)
        # self.log("Невалидные триплеты:", verbose=self.config.verbose)
        # valid_triplets = []
        # for triplet in triplets:
        #     #t_graph_exists = self.kg_model.graph_struct.db_conn.item_exist(triplet.id)
        #     r_graph_exists = self.kg_model.graph_struct.db_conn.item_exist(triplet.relation.id, id_type='relation')
        #     #sn_graph_exists = self.kg_model.graph_struct.db_conn.item_exist(triplet.start_node.id, id_type='node')
        #     #en_graph_exists = self.kg_model.graph_struct.db_conn.item_exist(triplet.end_node.id, id_type='node')

        #     r_vector_exists = self.kg_model.embeddings_struct.vectordbs['triplets'].item_exist(triplet.relation.id)
        #     #sn_vector_exists = self.kg_model.embeddings_struct.vectordbs['nodes'].item_exist(triplet.start_node.id)
        #     #en_vector_exists = self.kg_model.embeddings_struct.vectordbs['nodes'].item_exist(triplet.end_node.id)

        #     if not (r_graph_exists and r_graph_exists):
        #         self.log(f"* [graph - r:{r_graph_exists} | vector - r:{r_vector_exists}] {triplet}", verbose=self.config.verbose)
        #     else:
        #         valid_triplets.append(triplet)

        # self.log(f"RESULT:\n* валидных - {len(valid_triplets)} \n* невалидных - {len(triplets) - len(valid_triplets)}", verbose=self.config.verbose)

        self.log("STAGE #3.2 - TRIPLETS FILTERING...", verbose=self.config.verbose)
        if self.triplets_filter is not None:
            filtered_triplets = self.triplets_filter.apply_filter(query_info, triplets)
            self.log(f"RESULT: {len(filtered_triplets)}", verbose=self.config.verbose)
            for triplet in filtered_triplets:
                self.log(f"*[{triplet.id}] {triplet}", verbose=self.config.verbose)
        else:
            filtered_triplets = triplets
            self.log("Filtering stage was disabled. Continue.")

        if len(filtered_triplets) == 0:
            info.status = ReturnStatus.zero_retrieved_triplets
            info.message = STATUS_MESSAGE[info.status]

        self.log(f"STATUS: {STATUS_MESSAGE[info.status]}", verbose=self.config.verbose)

        return filtered_triplets, info
