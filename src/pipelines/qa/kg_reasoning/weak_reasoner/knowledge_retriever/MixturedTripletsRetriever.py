from dataclasses import dataclass, field
from typing import List, Union, Dict
from copy import deepcopy

from .utils import AbstractTripletsRetriever, BaseGraphSearchConfig
from .AStarTripletsRetriever import AStarGraphSearchConfig, AStarTripletsRetriever
from .BFSTripletsRetriever import BFSSearchConfig, BFSRetriever
from .NaiveBFSTripletsRetriever import NaiveBFSTripletsRetriever
from .BeamSearchTripletsRetriever import BeamSearchTripletsRetriever
from ......utils.data_structs import QueryInfo, Triplet, create_id
from ......kg_model import KnowledgeGraphModel
from ......utils import Logger

@dataclass
class MixturedGraphSearchConfig(BaseGraphSearchConfig):
    """Конфигурация комбинированного алгоритма извлечения триплетов из графа знаний.

    :param astar_config: Конфигурация A*-алгоритма поиска. Значение по умолчанию AStarGraphSearchConfig().
    :type astar_config: AStarGraphSearchConfig
    :param bfs_config: Конфигурация BFS-алгоритма поиска. Значение по умолчанию BFSSearchConfig().
    :type bfs_config: BFSSearchConfig
    """
    retriever1_name: str = 'astar'
    retriever1_config: Union[BaseGraphSearchConfig, Dict] = field(default_factory=lambda: AStarGraphSearchConfig())
    retriever2_name: str = 'bfs'
    retriever2_config: Union[BaseGraphSearchConfig, Dict] = field(default_factory=lambda: BFSSearchConfig())

class MixturedTripletsRetriever(AbstractTripletsRetriever):
    """Класс предназначен для извлечения триплетов из графа знаний с помощью комбинации BFS- и A*-алгоритмов поиска.

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param config: Конфигурация комбинированного алгоритма поиска. Значение по умолчанию MixturedGraphSearchConfig().
    :type config: MixturedGraphSearchConfig
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты. Значение по умолчанию Logger(LOG_PATH).
    :type log: Logger
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool
    """
    def __init__(self, kg_model: KnowledgeGraphModel, log: Logger, search_config: Union[MixturedGraphSearchConfig, Dict] = MixturedGraphSearchConfig(),
                 verbose: bool = False) -> None:
        self.log = log
        self.verbose = verbose

        if type(search_config) is Dict:
            search_config = MixturedGraphSearchConfig(**search_config)
        self.config = search_config

        self.available_retrievers = {
            'astar': AStarTripletsRetriever,
            'bfs': BFSRetriever,
            'naive_bfs': NaiveBFSTripletsRetriever,
            'beamsearch': BeamSearchTripletsRetriever
        }

        self.retriever1 = self.available_retrievers[search_config.retriever1_name]['class'](
            kg_model, log, search_config.retriever1_config, verbose)
        self.retriever2 = self.available_retrievers[search_config.retriever2_name]['class'](
            kg_model, log, search_config.retriever2_config, verbose)

    def get_relevant_triplets(self, query_info: QueryInfo) -> List[Triplet]:
        self.log("START KNOWLEDGE RETRIEVING ...", verbose=self.verbose)
        self.log(f"BASE_QUESTION ID: {create_id(query_info.query)}", verbose=self.verbose)
        self.log(f"BASE_QUESTION: {query_info.query}", verbose=self.verbose)

        triplets1 = self.retriever1.get_relevant_triplets(query_info)
        triplets2 = self.retriever2.get_relevant_triplets(query_info)

        self.log(f"Количество триплетов, извлечённых с помощью {self.config.retriever1_name}/{self.config.retriever2_name}: {len(triplets1)}/{len(triplets2)}",
                 verbose=self.verbose)

        # отбираем только уникальные триплеты (по их идентификаторам)
        unique_triplets = dict()
        for triplet in triplets1 + triplets2:
            unique_triplets[triplet.id] = deepcopy(triplet)

        return list(unique_triplets.values())
