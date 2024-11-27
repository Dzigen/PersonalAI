import pytest

import sys
sys.path.insert(0, "../../")

from src.utils import Triplet
from src.pipelines.memorize import LLMUpdator

from typing import List, Dict

@pytest.mark.parametrize("kg_triplets, triplets, expected_obsolete_ids", [
    # TODO
])
def test_find_simple(llm_updator: LLMUpdator, kg_triplets: List[Triplet], triplets: List[Triplet],
                     expected_obsolete_ids: List[str]):
    llm_updator.kg_model.clear()
    llm_updator.kg_model.create_triplets(kg_triplets)
    real_obsolete_ids  = llm_updator.find_hyper_obsolete_triplet_ids(triplets)

    assert expected_obsolete_ids == real_obsolete_ids
