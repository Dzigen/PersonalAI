import pytest

import sys
sys.path.insert(0, "../../")

@pytest.mark.parametrize("lang, base_triplet, incident_triplets, expected_thesis_ids, expected_status", [
    # TODO
])
def test_replace_thesis(replace_thesis_solver, lang, base_triplet, incident_triplets, expected_thesis_ids, expected_status):
    real_thesis_ids, real_status = replace_thesis_solver.solve(
        lang=lang, base_triplet=base_triplet, incident_triplets=incident_triplets)
    assert expected_thesis_ids == real_thesis_ids
    assert expected_status == real_status
