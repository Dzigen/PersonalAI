from .BFSTripletsRetriever import BFSRetriever
from .MixturedTripletsRetriever import MixturedTripletsRetriever
from .TripletsFilter import TripletsFilter
from .AStarTripletsRetriever import AStarTripletsRetriever

KR_MAIN_LOG_PATH = 'log/qa/knowledge_retriever/main'

AVAILABLE_TRIPLETS_RETRIEVERS  = {
    'astar': AStarTripletsRetriever,
    'bfs': BFSRetriever,
    'mixture': MixturedTripletsRetriever,
    'naive_bfs': NaiveBFSRetriever
}

AVAILABLE_TRIPLETS_FILTERS = {
    'naive': TripletsFilter
}
