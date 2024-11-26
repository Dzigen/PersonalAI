import pytest

import sys
sys.path.insert(0, "../../")

from src.utils import Triplet, ReturnStatus
from typing import List

@pytest.mark.parametrize("lang, base_triplet, incident_triplets, expected_triplet_ids, expected_status", [
    # TODO
])
def test_replace_thesis(replace_simple_solver, lang: str, base_triplet: Triplet, incident_triplets: List[Triplet],
                        expected_triplet_ids: List[str], expected_status: ReturnStatus):
    real_triplet_ids, real_status = replace_simple_solver.solve(
        lang=lang, base_triplet=base_triplet, incident_triplets=incident_triplets)
    assert expected_triplet_ids == real_triplet_ids
    assert expected_status == real_status
