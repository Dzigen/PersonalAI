from typing import Dict, Union
from .utils import AbstractTripletsRetriever, AbstractTriplesFilter, BaseGraphSearchConfig, BaseTripletsFilterConfig

from .traversal_methods import WaterCirclesRetriever, WaterCirclesSearchConfig
from .traversal_methods import MixturedTripletsRetriever, MixturedGraphSearchConfig
from .traversal_methods import AStarTripletsRetriever, AStarGraphSearchConfig
from .traversal_methods import NaiveBFSTripletsRetriever, NaiveBFSGraphSearchConfig
from .traversal_methods import NaiveTripletsRetriever, NaiveGraphSearchConfig
from .traversal_methods import BeamSearchTripletsRetriever, GraphBeamSearchConfig
from .filtering_methods import TripletsFilter, TripletsFilterConfig

KR_MAIN_LOG_PATH = 'log/qa/kg_reasoner/weak/knowledge_retriever/main'

AVAILABLE_TRIPLETS_RETRIEVERS: Dict[str, AbstractTripletsRetriever] = {
    'astar': AStarTripletsRetriever,
    'watercircles': WaterCirclesRetriever,
    'mixture': MixturedTripletsRetriever,
    'naive_bfs': NaiveBFSTripletsRetriever,
    'naive_retriever': NaiveTripletsRetriever,
    'beamsearch': BeamSearchTripletsRetriever
}

AVAILABLE_TRETRIEVERS_CONFIGS: Dict[str, BaseGraphSearchConfig] = {
    'astar': AStarGraphSearchConfig,
    'watercircles': WaterCirclesSearchConfig,
    'mixture': MixturedGraphSearchConfig,
    'naive_bfs': NaiveBFSGraphSearchConfig,
    'naive_retriever': NaiveGraphSearchConfig,
    'beamsearch': GraphBeamSearchConfig
}

AVAILABLE_TRIPLETS_FILTERS: Dict[str, AbstractTriplesFilter] = {
    'naive': TripletsFilter
}

AVAILABLE_TFILTERS_CONFIGS: Dict[str, BaseTripletsFilterConfig] = {
    'naive': TripletsFilterConfig
}
