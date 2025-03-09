from .BFSTripletsRetriever import BFSRetriever
from .MixturedTripletsRetriever import MixturedTripletsRetriever
from .TripletsFilter import TripletsFilter
from .AStarTripletsRetriever import AStarTripletsRetriever
from .NaiveBFSTripletsRetriever import NaiveBFSTripletsRetriever
from .NaiveTripletsRetriever import NaiveTripletsRetriever
from .BeamSearchTripletsRetriever import BeamSearchTripletsRetriever

KR_MAIN_LOG_PATH = 'log/qa/kg_reasoner/weak/knowledge_retriever/main'

AVAILABLE_TRIPLETS_RETRIEVERS  = {
    'astar': AStarTripletsRetriever,
    'bfs': BFSRetriever,
    'mixture': MixturedTripletsRetriever,
    'naive_bfs': NaiveBFSTripletsRetriever,
    'naive_retriever': NaiveTripletsRetriever,
    'beamsearch': BeamSearchTripletsRetriever
}

AVAILABLE_TRIPLETS_FILTERS = {
    'naive': TripletsFilter
}
