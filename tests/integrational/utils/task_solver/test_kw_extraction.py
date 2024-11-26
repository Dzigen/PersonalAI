import pytest

import sys
sys.path.insert(0, "../../")

@pytest.mark.parametrize("lang, query, expected_entities, expected_status", [
    # TODO
])
def test_kw_extractor(kwe_solver, lang, query, expected_entities, expected_status):
    real_entities, real_status = kwe_solver.solve(lang=lang, query=query)
    assert expected_entities == real_entities
    assert expected_status == real_status
