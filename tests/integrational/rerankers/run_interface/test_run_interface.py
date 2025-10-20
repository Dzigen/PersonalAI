import pytest
from typing import List, Union
import sys
sys.path.insert(0, "../")

from src.rerankers.methods.utils import AbstractRerankerModule
from src.rerankers.utils import BaseRerankerModuleConfig
from src.db_drivers.vector_driver import VectorComposer, VectorDBInstance

from .cases import POPULATED_RUN_TEST_CASES

@pytest.mark.parametrize("reranker_method, reranker_config, query, top_k, subset_ids, includes, return_with_embeddings, return_sparse, return_with_scores, exception",
                         POPULATED_RUN_TEST_CASES)
def test_run(reranker_method: AbstractRerankerModule, reranker_config: BaseRerankerModuleConfig,
             query: str, top_k: int, subset_ids: Union[None, List[str]], includes: List[str],
             return_with_embeddings: bool, return_sparse: bool, return_with_scores: bool, exception: bool,
             vector_composer: VectorComposer):

    reranker: AbstractRerankerModule = reranker_method(reranker_config, vector_composer)

    try:
        real_output = reranker.run(
            query=query, top_k=top_k, includes=includes, subset_ids=subset_ids,
            return_with_embeddings=return_with_embeddings, return_with_scores=return_with_scores)
    except (ValueError, AssertionError) as e:
        assert exception
    else:
        assert not exception

        # top_k check
        assert len(real_output) <= top_k

        # subset_ids check
        if subset_ids is not None:
            real_ids = list(map(lambda item: item[1].id if type(item) is tuple else item.id, real_output))
            containing_ids = set(subset_ids).intersection(set(real_ids))
            assert len(containing_ids) == len(real_ids)

        # includes check
        for raw_item in real_output:
            item = raw_item[1] if type(raw_item) is tuple else raw_item
            for field_name in includes:
                assert getattr(item, field_name[:-1]) is not None

        for raw_item in real_output:
            print(reranker_config)
            item = raw_item[1] if type(raw_item) is tuple else raw_item
            # return_with_embeddings check
            if return_with_embeddings:
                if return_sparse:
                    assert item.embedding is None
                else:
                    assert item.embedding is not None
            else:
                assert item.embedding is None

            # return_with_scores check
            if return_with_scores:
                assert (type(raw_item) is tuple) and (type(raw_item[0]) is float)
            else:
                assert type(raw_item) is VectorDBInstance
