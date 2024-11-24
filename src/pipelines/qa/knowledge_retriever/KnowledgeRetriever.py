from .utils import AbstractTriplesFilter, AbstractTripletsRetriever, RETRIEVER_LOG_PATH, BaseGraphSearchConfig, BaseTripletsFilterConfig
from .TripletsFilter import TripletsFilterConfig, TripletsFilter
from .AStarTripletsRetriever import AStarTripletsRetriever, AStarGraphSearchConfig
from .BFSTripletsRetriever import BFSRetriever, BFSSearchConfig
from .MixturedTripletsRetriever import MixturedTripletsRetriever, MixturedGraphSearchConfig
from ...utils.data_structs import QueryInfo, Triplet
from ...knowledge_graph_model import KnowledgeGraphModel
from ...db_drivers.kv_driver import KeyValueDriver, KeyValueDriverConfig
from ...utils import Logger, ReturnStatus, ReturnInfo
from ...utils.errors import QA_ZERO_RETRIEVED_TRIPLETS_MSG

from dataclasses import dataclass, field
from typing import List, Tuple

AVAILABLE_TRIPLETS_RETRIEVERS  = {
    'astar': AStarTripletsRetriever,
    'bfs': BFSRetriever,
    'mixture': MixturedTripletsRetriever
}

AVAILABLE_TRIPLETS_FILTERS = {
    'naive': TripletsFilter
}

@dataclass
class KnowledgeRetrieverConfig:
    """Конфигурация "Knowledge Retriever"-стадии.

    :param retriever_method: TODO. Значение по умолчанию 'astar'.
    :type retriever_method: str
    :param retriever_config: TODO. Значение по умолчанию AStarGraphSearchConfig().
    :type retriever_config: BaseGraphSearchConfig
    :param filter_method: TODO. Значение по умолчанию 'naive'.
    :type filter_method: str
    :param filter_config: TODO. Значение по умолчанию TripletsFilterConfig().
    :type filter_config: BaseTripletsFilterConfig
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой комопненты. Значение по умолчанию Logger(RETRIEVER_LOG_PATH).
    :type log: Logger
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool
    """
    retriever_method: str = 'astar'
    retriever_config: BaseGraphSearchConfig = field(default_factory=lambda: AStarGraphSearchConfig())
    filter_method: str = 'naive'
    filter_config: BaseTripletsFilterConfig = field(default_factory=lambda: TripletsFilterConfig())
    log: Logger = field(default_factory=lambda: Logger(RETRIEVER_LOG_PATH))
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

        :param query_info: Структура данных, которая хранит user-вопрос и связанную с ним инфомрацию.
        :type query_info: QueryInfo
        :return: Кортеж из двух объектов: (1) список релевантных user-вопросу триплетов; (2) статус завершения операции с пояснительной информацией.
        :rtype: Tuple[List[Triplet], ReturnInfo]
        """
        info = ReturnInfo()
        self.log("stage #3.1 - extracting triplets...", verbose=self.config.verbose)
        triplets = self.graph_retriever.get_relevant_triplets(query_info)
        self.log(f"Количество извлечённых триплетов: {len(triplets)}", verbose=self.config.verbose)

        self.log("stage #3.2 - filtering triplets...", verbose=self.config.verbose)
        filtered_triplets = self.triplets_filter.apply_filter(query_info, triplets)
        self.log(f"Количество триплетов после фильтрации: {len(filtered_triplets)}", verbose=self.config.verbose)

        if len(filtered_triplets) == 0:
            info.status = ReturnStatus.zero_retrieved_triplets
            info.message = QA_ZERO_RETRIEVED_TRIPLETS_MSG

        return filtered_triplets, info
