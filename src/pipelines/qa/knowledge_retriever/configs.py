from .BFSTripletsRetriever import BFSRetriever
from .MixturedTripletsRetriever import MixturedTripletsRetriever
from .TripletsFilter import TripletsFilter
from .AStarTripletsRetriever import AStarTripletsRetriever
from .NaiveTripletsRetriever import NaiveTripletsRetriever

KR_MAIN_LOG_PATH = 'log/qa/knowledge_retriever/main'

AVAILABLE_TRIPLETS_RETRIEVERS  = {
    'astar': AStarTripletsRetriever,
    'bfs': BFSRetriever,
    'mixture': MixturedTripletsRetriever,
    'naive': NaiveTripletsRetriever
}

AVAILABLE_TRIPLETS_FILTERS = {
    'naive': TripletsFilter,
    'disable': None
}
