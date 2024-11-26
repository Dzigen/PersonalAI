import pytest

import sys
sys.path.insert(0, "../../")

from src.utils import Triplet, ReturnStatus
from typing import List

@pytest.mark.parametrize("lang, base_triplet, incident_triplets, expected_thesis_ids, expected_status", [
    # TODO
])
def test_replace_thesis(replace_thesis_solver, lang: str, base_triplet: Triplet, incident_triplets: List[Triplet],
                        expected_thesis_ids: List[str], expected_status: ReturnStatus):
    real_thesis_ids, real_status = replace_thesis_solver.solve(
        lang=lang, base_triplet=base_triplet, incident_triplets=incident_triplets)
    assert expected_thesis_ids == real_thesis_ids
    assert expected_status == real_status
