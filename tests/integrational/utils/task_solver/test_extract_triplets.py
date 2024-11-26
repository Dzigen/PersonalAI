import pytest

import sys
sys.path.insert(0, "../../")

@pytest.mark.parametrize("lang, text, rel_prop, expected_triplets, expected_status", [
    # TODO
])
def test_extract_thesises(etriplets_solver, lang, text, rel_prop, expected_triplets, expected_status):
    real_triplets, real_status = etriplets_solver.solve(lang, text=text, rel_prop=rel_prop)
    assert expected_triplets == real_triplets
    assert expected_status == real_status
