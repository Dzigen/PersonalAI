import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from copy import deepcopy

from src.rerankers.methods import MultiStepRerankerConfig
from src.rerankers.methods.MultiStepReranker import RerankStep, RerankingType

AVAILABLE_DENSEDB_NAMES = ['dense_chroma', 'dense_milvus']
AVAILABLE_SPARSEDB_NAMES = ['bm25_opensearch', 'bm25_elasticsearch', 'bm25_inmemory']


# reranker_config, query, topk_k, output_amount, approximate_output, exception
MULTISTEP_RUN_TEST_CASES = [
    # 1. полное совпадение query и passage-значения в бд
    [MultiStepRerankerConfig(reranking_sequence=[RerankStep(type=RerankingType.retriever, name=..., fetch_n=10), RerankStep(type=RerankingType.retriever, name=..., fetch_n=1)]), 'Rose', 1, ['Rose'], False],
    # 2. query- и существующее passage-значение отличаются только регистром
    [MultiStepRerankerConfig(reranking_sequence=[RerankStep(type=RerankingType.retriever, name=..., fetch_n=10), RerankStep(type=RerankingType.retriever, name=..., fetch_n=1)]), 'elephant', 1, ['Elephant'], False],
    # 3. извлекается несколько "wild animals"-объектов
    [MultiStepRerankerConfig(reranking_sequence=[RerankStep(type=RerankingType.retriever, name=..., fetch_n=10), RerankStep(type=RerankingType.retriever, name=..., fetch_n=3)]), 'wild animals', 3, ['Lion', 'Tiger', 'Elephant', 'Giraffe', 'Zebra', 'Wild cat'], False],
    # 4. извлекается несколько "domestic animals"-объектов
    [MultiStepRerankerConfig(reranking_sequence=[RerankStep(type=RerankingType.retriever, name=..., fetch_n=10), RerankStep(type=RerankingType.retriever, name=..., fetch_n=3)]), 'domestic animals', 3, ['Dog', 'Cat', 'Horse', 'Cow', 'Sheep', 'Rabbit', 'Pig', 'Domestic wolf'], False],
    # TODO
]

MULTISTEP_POPULATED_RUN_TEST_CASES = []
for dense_name in AVAILABLE_DENSEDB_NAMES:
    for sparse_name in AVAILABLE_SPARSEDB_NAMES:
        for i in range(len(MULTISTEP_RUN_TEST_CASES)):
            modif_testcase = deepcopy(MULTISTEP_RUN_TEST_CASES[i])
            modif_testcase[0].reranking_sequence[0].name = sparse_name
            modif_testcase[0].reranking_sequence[1].name = dense_name
            modif_testcase.append('vector_composer')
            MULTISTEP_POPULATED_RUN_TEST_CASES.append(modif_testcase)
