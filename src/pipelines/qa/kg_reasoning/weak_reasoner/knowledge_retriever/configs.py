from .traversal_methods import WaterCirclesRetriever, WaterCirclesSearchConfig
from .traversal_methods import MixturedTripletsRetriever, MixturedGraphSearchConfig
from .traversal_methods import AStarTripletsRetriever, AStarGraphSearchConfig
from .traversal_methods import NaiveBFSTripletsRetriever, NaiveBFSGraphSearchConfig
from .traversal_methods import NaiveTripletsRetriever, NaiveGraphSearchConfig
from .traversal_methods import BeamSearchTripletsRetriever, GraphBeamSearchConfig
from .filtering_methods import TripletsFilter, TripletsFilterConfig

KR_MAIN_LOG_PATH = 'log/qa/kg_reasoner/weak/knowledge_retriever/main'

AVAILABLE_TRIPLETS_RETRIEVERS = {
    'astar': {
        'config': AStarGraphSearchConfig,
        'class': AStarTripletsRetriever},

    'watercircles': {
        'config': WaterCirclesSearchConfig,
        'class': WaterCirclesRetriever},

    'mixture': {
        'config': MixturedGraphSearchConfig,
        'class': MixturedTripletsRetriever},

    'naive_bfs': {
        'config': NaiveBFSGraphSearchConfig,
        'class': NaiveBFSTripletsRetriever},

    'naive_retriever': {
        'config': NaiveGraphSearchConfig,
        'class': NaiveTripletsRetriever},

    'beamsearch': {
        'config': GraphBeamSearchConfig,
        'class': BeamSearchTripletsRetriever}
}

AVAILABLE_TRIPLETS_FILTERS = {
    'naive': {
        'config': TripletsFilterConfig,
        'class': TripletsFilter}
}
