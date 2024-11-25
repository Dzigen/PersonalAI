from dataclasses import dataclass, field
from typing import List
from copy import deepcopy

from .utils import AbstractTripletsRetriever, BaseGraphSearchConfig
from .AStarTripletsRetriever import AStarGraphSearchConfig, AStarTripletsRetriever
from .BFSTripletsRetriever import BFSSearchConfig, BFSRetriever
from ....utils.data_structs import QueryInfo, Triplet
from ....knowledge_graph_model import KnowledgeGraphModel
from ....utils import Logger

@dataclass
class MixturedGraphSearchConfig(BaseGraphSearchConfig):
    """Конфигурация комбинированного алгоритма по исзлечению триплетов из графа знаний.

    :param astar_config: Конфигурация A*-алгоритиа поиска. Значение по умолчанию AStarGraphSearchConfig().
    :type astar_config: AStarGraphSearchConfig
    :param bfs_config: Конфигурация BFS-алгоритма поиска. Значение по умолчанию BFSSearchConfig().
    :type bfs_config: BFSSearchConfig
    """
    astar_config: AStarGraphSearchConfig = field(default_factory=lambda: AStarGraphSearchConfig())
    bfs_config: BFSSearchConfig = field(default_factory=lambda: BFSSearchConfig())

class MixturedTripletsRetriever(AbstractTripletsRetriever):
    """Класс предназначен для извлечения триплетов из графа знаний с помощью комбинации BFS- и A*-алгоритмов поиска.

    :param kg_model: Модель памяти (графа знаний) ассистента.
    :type kg_model: KnowledgeGraphModel
    :param config: Конфигурация комбинирванного алгоритма поиска. Значение по умолчанию MixturedGraphSearchConfig().
    :type config: MixturedGraphSearchConfig
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой комопненты. Значение по умолчанию Logger(LOG_PATH).
    :type log: Logger
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool
    """
    def __init__(self, kg_model: KnowledgeGraphModel, log: Logger, search_config: MixturedGraphSearchConfig = MixturedGraphSearchConfig(),
                 verbose: bool = False) -> None:
        self.log = log
        self.verbose = verbose

        self.astar_searcher = AStarTripletsRetriever(kg_model, log, search_config.astar_config, verbose)
        self.bfs_searcher = BFSRetriever(kg_model, log, search_config.bfs_config, verbose)

    def get_relevant_triplets(self, query_info: QueryInfo) -> List[Triplet]:
        astar_triplets = self.astar_searcher.get_relevant_triplets(query_info)
        bfs_triplets = self.bfs_searcher.get_relevant_triplets(query_info)

        self.log(f"Количество триплетов, извлечённых с помощью A*/BFS: {len(astar_triplets)}/{len(bfs_triplets)}",
                 verbose=self.verbose)

        # отбираем только уникальные триплеты (по их идентификаторам)
        unique_triplets = dict()
        for triplet in astar_triplets + bfs_triplets:
            unique_triplets[triplet.id] = deepcopy(triplet)

        return unique_triplets.values()
