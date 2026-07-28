import sys
from copy import deepcopy
from functools import reduce
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.pipelines.qa.knowledge_retriever.traversal_methods import \
    AStarGraphSearchConfig, GraphBeamSearchConfig, NaiveGraphSearchConfig, \
        WaterCirclesSearchConfig, MixturedGraphSearchConfig, NaiveBFSGraphSearchConfig

from src.pipelines.qa.knowledge_retriever.filtering_methods import TripletsFilterConfig

from ...cases import QUESTIONS
from ..cases import KW_ENTITIES

LANGUAGES = ['ru', 'en']

#
KG_TRAVERSE_METHODS = [
    # Astar
    ['astar', AStarGraphSearchConfig()],
    # BeamSearch
    ['beamsearch', GraphBeamSearchConfig()],
    # BFS
    ['naive_bfs', NaiveBFSGraphSearchConfig()],
    # Naive Retrieve
    ['naive_retriever', NaiveGraphSearchConfig()],
    # WaterCircles
    ['watercircles', WaterCirclesSearchConfig()],
    # Mixture (Astar + BeamSearch)
    ['mixture', MixturedGraphSearchConfig(
        retriever1_name='astar',
        retriever1_config=AStarGraphSearchConfig(),
        retriever2_name='beamsearch',
        retriever2_config=GraphBeamSearchConfig()
    )],
    # Mixture (Astar + BFS)
    ['mixture', MixturedGraphSearchConfig(
        retriever1_name='astar',
        retriever1_config=AStarGraphSearchConfig(),
        retriever2_name='naive_bfs',
        retriever2_config=NaiveBFSGraphSearchConfig()
    )],
    # Mixture (Astar + Naive Retrieve)
    ['mixture', MixturedGraphSearchConfig(
        retriever1_name='astar',
        retriever1_config=AStarGraphSearchConfig(),
        retriever2_name='naive_retriever',
        retriever2_config=NaiveGraphSearchConfig()
    )],
    # Mixture (Astar + WaterCircles)
    ['mixture', MixturedGraphSearchConfig(
        retriever1_name='astar',
        retriever1_config=AStarGraphSearchConfig(),
        retriever2_name='watercircles',
        retriever2_config=WaterCirclesSearchConfig()
    )],
    # Mixture (BeamSearch + BFS)
    ['mixture', MixturedGraphSearchConfig(
        retriever1_name='beamsearch',
        retriever1_config=GraphBeamSearchConfig(),
        retriever2_name='naive_bfs',
        retriever2_config=NaiveBFSGraphSearchConfig()
    )],
    # Mixture (BeamSearch + Naive Retrieve)
    ['mixture', MixturedGraphSearchConfig(
        retriever1_name='beamsearch',
        retriever1_config=GraphBeamSearchConfig(),
        retriever2_name='naive_retriever',
        retriever2_config=NaiveGraphSearchConfig()
    )],
    # Mixture (BeamSearch + WaterCircles)
    ['mixture', MixturedGraphSearchConfig(
        retriever1_name='beamsearch',
        retriever1_config=GraphBeamSearchConfig(),
        retriever2_name='watercircles',
        retriever2_config=WaterCirclesSearchConfig()
    )],
    # Mixture (BFS + Naive Retrieve)
    ['mixture', MixturedGraphSearchConfig(
        retriever1_name='naive_bfs',
        retriever1_config=NaiveBFSGraphSearchConfig(),
        retriever2_name='naive_retriever',
        retriever2_config=NaiveGraphSearchConfig()
    )],
    # Mixture (BFS + WaterCircles)
    ['mixture', MixturedGraphSearchConfig(
        retriever1_name='naive_bfs',
        retriever1_config=NaiveBFSGraphSearchConfig(),
        retriever2_name='watercircles',
        retriever2_config=WaterCirclesSearchConfig()
    )],
    # Mixture (Naive Retrieve + WaterCircles)
    ['mixture', MixturedGraphSearchConfig(
        retriever1_name='naive_retriever',
        retriever1_config=NaiveGraphSearchConfig(),
        retriever2_name='watercircles',
        retriever2_config=WaterCirclesSearchConfig()
    )]
]

FILTER_METHODS = [
    [None, None],
    ['naive', TripletsFilterConfig(max_k=30)]
]

POPULATES_KG_RETRIEVER_CONFIGS = []
for traversal_method_config in KG_TRAVERSE_METHODS:
    for filter_method_config in FILTER_METHODS:
        t_name, t_config = traversal_method_config[0], deepcopy(traversal_method_config[1])
        f_name, f_config = filter_method_config[0], deepcopy(filter_method_config[1])
        POPULATES_KG_RETRIEVER_CONFIGS.append([t_name, t_config, f_name, f_config])
#
POPULATES_KG_TRAVERSE_TEST_CASES = []
for retriever_config in POPULATES_KG_RETRIEVER_CONFIGS:
    rconfig_copy = deepcopy(retriever_config)
    for language in LANGUAGES:
        for entities, query in zip(KW_ENTITIES[language], QUESTIONS[language]):
            POPULATES_KG_TRAVERSE_TEST_CASES.append(rconfig_copy + [query, entities, language])
