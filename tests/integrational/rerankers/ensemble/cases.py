import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from copy import deepcopy
from src.rerankers.methods import EnsembleFusionRerankerConfig
from src.rerankers.methods.EnsembleFusionReranker import RetrieverConfig

AVAILABLE_DENSEDB_NAMES = ['dense_chroma', 'dense_milvus']
AVAILABLE_SPARSEDB_NAMES = ['bm25_opensearch', 'bm25_elasticsearch', 'bm25_inmemory']


# reranker_config, query, topk_k, output_amount, approximate_output, exception
ENSEMBLE_RUN_TEST_CASES = [
    # 1. полное совпадение query и passage-значения в бд
    [EnsembleFusionRerankerConfig(vdb_names=..., retriever_configs=[RetrieverConfig(fetch_n=5),RetrieverConfig(fetch_n=5)]), 'Rose', 1, ['Rose'], False],
    # 2. query- и существующее passage-значение отличаются только регистром
    [EnsembleFusionRerankerConfig(vdb_names=..., retriever_configs=[RetrieverConfig(fetch_n=5),RetrieverConfig(fetch_n=5)]), 'elephant', 1, ['Elephant'], False],
    # 3. извлекается несколько "wild animals"-объектов
    [EnsembleFusionRerankerConfig(vdb_names=..., retriever_configs=[RetrieverConfig(fetch_n=5),RetrieverConfig(fetch_n=5)]), 'wild animals', 3, ['Lion', 'Tiger', 'Elephant', 'Giraffe', 'Zebra', 'Wild cat'], False],
    # 4. извлекается несколько "domestic animals"-объектов
    [EnsembleFusionRerankerConfig(vdb_names=..., retriever_configs=[RetrieverConfig(fetch_n=5),RetrieverConfig(fetch_n=5)]), 'domestic animals', 3, ['Dog', 'Cat', 'Horse', 'Cow', 'Sheep', 'Rabbit', 'Pig', 'Domestic wolf'], False],
    # TODO
]

ENSEMBLE_POPULATED_RUN_TEST_CASES = []
for dense_name in AVAILABLE_DENSEDB_NAMES:
    for sparse_name in AVAILABLE_SPARSEDB_NAMES:
        for i in range(len(ENSEMBLE_RUN_TEST_CASES)):
            modif_testcase = deepcopy(ENSEMBLE_RUN_TEST_CASES[i])
            modif_testcase[0].vdb_names = [sparse_name, dense_name]
            modif_testcase.append('vector_composer')
            ENSEMBLE_POPULATED_RUN_TEST_CASES.append(modif_testcase)
