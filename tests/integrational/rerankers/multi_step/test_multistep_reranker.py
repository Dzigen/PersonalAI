import pytest
from typing import List
import sys
sys.path.insert(0, "../")

from src.rerankers.methods import MultiStepRerankerConfig, MultiStepReranker
from src.db_drivers.vector_driver import VectorComposer

from .cases import MULTISTEP_POPULATED_RUN_TEST_CASES

@pytest.mark.parametrize("reranker_config, query, top_k, approximate_texts, exception",
                         MULTISTEP_POPULATED_RUN_TEST_CASES)
def test_run(reranker_config: MultiStepRerankerConfig, query: str, top_k: int,
             approximate_texts: List[str], exception: bool, vector_composer: VectorComposer):

    reranker = MultiStepReranker(reranker_config, vector_composer)

    try:
        real_output = reranker.run(query=query, top_k=top_k)
    except (ValueError, AssertionError) as e:
        assert exception
    else:
        assert not exception

    print(real_output)

    real_texts = list(map(lambda item: item.document, real_output))
    assert len(real_texts) <= top_k

    if approximate_texts is not None:
        real_percent_match = round(sum([r_texts in approximate_texts for r_texts in real_texts]) / len(real_texts),2)
        assert real_percent_match > 0
