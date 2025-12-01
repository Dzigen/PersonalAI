import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from copy import deepcopy

from src.rerankers.methods import SingleStepRerankerConfig


AVAILABLE_VECTORDB_NAMES = [
    'dense_chroma', 'dense_inmemory', 'dense_elasticsearch', 'dense_weaviate', 'dense_qdrant', #'dense_opensearch',
    'bm25_opensearch', 'bm25_elasticsearch', 'bm25_inmemory', 'bm25_weaviate'
]

SINGLESTEP_RERANKER_CONFIGS = []
for name in AVAILABLE_VECTORDB_NAMES:
    SINGLESTEP_RERANKER_CONFIGS.append(
        SingleStepRerankerConfig(vdb_name=name, threshold=None, fetch_n=5)
    )

# reranker_config, query, topk_k, approximate_output, exception
SINGLESTEP_RUN_TEST_CASES = [
    # 1. полное совпадение query и passage-значения в бд
    [..., 'Rose', 1, ['Rose'], False],
    # 2. query- и существующее passage-значение отличаются только регистром
    [..., 'elephant', 1, ['Elephant'], False],
    # 3. извлекается несколько "wild animals"-объектов
    [..., 'wild animals', 3, ['Lion', 'Tiger', 'Elephant', 'Giraffe', 'Zebra', 'Wild cat'], False],
    # 4. извлекается несколько "domestic animals"-объектов
    [..., 'domestic animals', 3, ['Dog', 'Cat', 'Horse', 'Cow', 'Sheep', 'Rabbit', 'Pig', 'Domestic wolf'], False]
    # 5. threshold = 0
    # TODO
    # 6. threshold = 1 and out-of-scope query
    # TODO
    # 7. threshold < 0
    # TODO
    # 8. fetch_n = 0
    # TODO
    # 9. fetch_n < 0
    # TODO
    # 10. top_k = 0
    # TODO
    # 11. top_k < 0
    # TODO
    # 12. неверный формат query
    # TODO
    # 13. vdb_conn_name-значения нет в vector-composer объекте
    # TODO
]

SINGLESTEP_POPULATED_RUN_TEST_CASES = []
for reranker_config in SINGLESTEP_RERANKER_CONFIGS:
    for test_case in SINGLESTEP_RUN_TEST_CASES:
        modif_testcase = deepcopy(test_case)
        modif_testcase[0] = reranker_config

        SINGLESTEP_POPULATED_RUN_TEST_CASES.append(modif_testcase)
