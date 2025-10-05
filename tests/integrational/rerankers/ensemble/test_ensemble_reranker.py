import pytest
from typing import List
import sys
sys.path.insert(0, "../")

from src.rerankers.methods import EnsembleFusionReranker, EnsembleFusionRerankerConfig
from src.db_drivers.vector_driver import VectorComposer

from .cases import ENSEMBLE_POPULATED_RUN_TEST_CASES

@pytest.mark.parametrize("reranker_config, query, top_k, approximate_texts, exception, vector_composer",
                         ENSEMBLE_POPULATED_RUN_TEST_CASES, indirect=['vector_composer'])
def test_run(reranker_config: EnsembleFusionRerankerConfig, query: str, top_k: int,
             approximate_texts: List[str], exception: bool, vector_composer: VectorComposer):

    reranker = EnsembleFusionReranker(reranker_config, vector_composer)

    try:
        real_output = reranker.run(query=query, top_k=top_k)
    except (ValueError, AssertionError) as e:
        assert exception
    else:
        assert not exception

    real_texts = list(map(lambda item: item.document, real_output))
    assert len(real_texts) <= top_k

    if approximate_texts is not None:
        real_percent_match = round(len(real_texts) / sum([r_texts in approximate_texts for r_texts in real_texts]),2)
        assert real_percent_match > 0
