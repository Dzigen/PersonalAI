import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from copy import deepcopy

from src.rerankers.methods import SingleStepRerankerConfig


AVAILABLE_VECTORDB_NAMES = [
    'dense_chroma', 'dense_milvus',
    'bm25_opensearch', 'bm25_elasticsearch', 'bm25_inmemory'
]

# reranker_config, query, topk_k, approximate_output, exception
SINGLESTEP_RUN_TEST_CASES = [
    # 1. полное совпадение query и passage-значения в бд
    [SingleStepRerankerConfig(vdb_name=..., threshold=None, fetch_n=1), 'Rose', 1, ['Rose'], False],
    # 2. query- и существующее passage-значение отличаются только регистром
    [SingleStepRerankerConfig(vdb_name=..., threshold=None, fetch_n=1), 'elephant', 1, ['Elephant'], False],
    # 3. извлекается несколько "wild animals"-объектов
    [SingleStepRerankerConfig(vdb_name=..., threshold=None, fetch_n=3), 'wild animals', 3, ['Lion', 'Tiger', 'Elephant', 'Giraffe', 'Zebra', 'Wild cat'], False],
    # 4. извлекается несколько "domestic animals"-объектов
    [SingleStepRerankerConfig(vdb_name=..., threshold=None, fetch_n=3), 'domestic animals', 3, ['Dog', 'Cat', 'Horse', 'Cow', 'Sheep', 'Rabbit', 'Pig', 'Domestic wolf'], False],
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
for db_name in AVAILABLE_VECTORDB_NAMES:
    for i in range(len(SINGLESTEP_RUN_TEST_CASES)):
        modif_testcase = deepcopy(SINGLESTEP_RUN_TEST_CASES[i])
        modif_testcase[0].vdb_name = db_name
        modif_testcase.append('vector_composer')

        SINGLESTEP_POPULATED_RUN_TEST_CASES.append(modif_testcase)
