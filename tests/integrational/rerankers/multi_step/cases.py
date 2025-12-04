import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from copy import deepcopy

from src.rerankers.methods import MultiStepRerankerConfig
from src.rerankers.methods.MultiStepReranker import RerankStep, RerankingType

AVAILABLE_DENSEDB_NAMES = ['dense_chroma', 'dense_inmemory', 'dense_elasticsearch', 'dense_weaviate', 'dense_qdrant', 'dense_opensearch']
AVAILABLE_SPARSEDB_NAMES = ['bm25_opensearch', 'bm25_elasticsearch', 'bm25_inmemory', 'bm25_weaviate']

MULTISTEP_RERANKER_CONFIGS = []
for dense_name in AVAILABLE_DENSEDB_NAMES:
    for sparse_name in AVAILABLE_SPARSEDB_NAMES:
        MULTISTEP_RERANKER_CONFIGS.append(
            MultiStepRerankerConfig(
                reranking_sequence=[
                    RerankStep(type=RerankingType.retriever, name=sparse_name, fetch_n=10),
                    RerankStep(type=RerankingType.retriever, name=dense_name, fetch_n=5)
                ]
            )
        )

# reranker_config, query, topk_k, output_amount, approximate_output, exception
MULTISTEP_RUN_TEST_CASES = [
    # 1. полное совпадение query и passage-значения в бд
    [..., 'Rose', 1, ['Rose'], False],
    # 2. query- и существующее passage-значение отличаются только регистром
    [..., 'elephant', 1, ['Elephant'], False],
    # 3. извлекается несколько "wild animals"-объектов
    [..., 'wild animals', 3, ['Lion', 'Tiger', 'Elephant', 'Giraffe', 'Zebra', 'Wild cat'], False],
    # 4. извлекается несколько "domestic animals"-объектов
    [..., 'domestic animals', 3, ['Dog', 'Cat', 'Horse', 'Cow', 'Sheep', 'Rabbit', 'Pig', 'Domestic wolf'], False],
    # TODO
]

MULTISTEP_POPULATED_RUN_TEST_CASES = []
for reranker_config in MULTISTEP_RERANKER_CONFIGS:
    for test_case in MULTISTEP_RUN_TEST_CASES:
        modif_testcase = deepcopy(test_case)
        modif_testcase[0] = reranker_config
        MULTISTEP_POPULATED_RUN_TEST_CASES.append(modif_testcase)
