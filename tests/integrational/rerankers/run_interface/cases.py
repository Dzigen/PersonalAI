import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from copy import deepcopy

from src.rerankers.methods import EnsembleFusionReranker, MultiStepReranker, SingleStepReranker
from src.rerankers.methods.MultiStepReranker import RerankingType

from ..ensemble.cases import ENSEMBLE_RERANKER_CONFIGS
from ..single_step.cases import SINGLESTEP_RERANKER_CONFIGS
from ..multi_step.cases import MULTISTEP_RERANKER_CONFIGS
from ..conftest import ITEM_IDS

# reranker_method, reranker_config, query, top_k, subset_ids, includes, return_with_embeddings,
# return_sparse, return_with_scores, exception, vector_composer
RUN_TEST_CASES = [
    # 1. positive test
    [None, None, 'Rose', 3, None, ['documents', 'metadatas'], False, None, False, False],
    # 2. top_k == 0
    [None, None, 'Elephant', 0, None, ['documents', 'metadatas'], False, None, False, False],
    # 3. not existed subset_ids
    [None, None, 'Olivia', 3, ['1111111111','2222222222','333333333'], ['documents', 'metadatas'], False, None, False, False],
    # 4. not valid subset_ids
    [None, None, 'Rose', 3, [532,4654,575], ['documents', 'metadatas'], False, None, False, True],
    # 5. valid_subset_ids
    [None, None, 'Elephant', 3, ITEM_IDS[:5], ['documents', 'metadatas'], False, None, False, False],
    # 6. not include documents, metadata
    [None, None, 'Olivia', 3, None, [], False, None, False, False],
    # 7. retrun with scores
    [None, None, 'Rose', 3, None, ['documents', 'metadatas'], False, None, True, False],
    # 8. return with embeddings
    [None, None, 'Elephant', 3, None, ['documents', 'metadatas'], True, None, False, False]
]

POPULATED_RUN_TEST_CASES = []

#
for ensemble_config in ENSEMBLE_RERANKER_CONFIGS:
    for test_case in RUN_TEST_CASES:
        modif_tcase = deepcopy(test_case)

        modif_tcase[0] = EnsembleFusionReranker
        modif_tcase[1] = ensemble_config
        if modif_tcase[6] or modif_tcase[8]:
            for vdb_name in ensemble_config.vdb_names:
                new_tcase = deepcopy(modif_tcase)
                if new_tcase[6]:
                    new_tcase[6] = vdb_name
                if new_tcase[8]:
                    new_tcase[8] = vdb_name

                if vdb_name.startswith('dense'):
                    new_tcase[7] = False
                else:
                    new_tcase[7] = True

                POPULATED_RUN_TEST_CASES.append(new_tcase)

        else:
            POPULATED_RUN_TEST_CASES.append(modif_tcase)

#
for singlestep_config in SINGLESTEP_RERANKER_CONFIGS:
    for test_case in RUN_TEST_CASES:
        modif_tcase = deepcopy(test_case)

        modif_tcase[0] = SingleStepReranker
        modif_tcase[1] = singlestep_config

        if modif_tcase[6]:
            if singlestep_config.vdb_name.startswith('dense'):
                modif_tcase[7] = False
            else:
                modif_tcase[7] = True

        POPULATED_RUN_TEST_CASES.append(modif_tcase)

#
for multistep_config in MULTISTEP_RERANKER_CONFIGS:
    for test_case in RUN_TEST_CASES:
        modif_tcase = deepcopy(test_case)

        modif_tcase[0] = MultiStepReranker
        modif_tcase[1] = multistep_config
        if modif_tcase[6] or modif_tcase[8]:
            vdb_names = [item.name for item in multistep_config.reranking_sequence if item.type == RerankingType.retriever]
            for vdb_name in vdb_names:
                new_tcase = deepcopy(modif_tcase)

                if new_tcase[6]:
                    new_tcase[6] = vdb_name
                if new_tcase[8]:
                    new_tcase[8] = vdb_name

                if vdb_name.startswith('dense'):
                    new_tcase[7] = False
                else:
                    new_tcase[7] = True
                POPULATED_RUN_TEST_CASES.append(new_tcase)

        else:
            POPULATED_RUN_TEST_CASES.append(modif_tcase)
