import pytest

import sys
sys.path.insert(0, "../../")

from src.utils import ReturnStatus
from typing import List

@pytest.mark.parametrize("lang, query, expected_entities, expected_status", [
    # TODO
])
def test_kw_extractor(kwe_solver, lang: str, query: str, expected_entities: List[str], expected_status: ReturnStatus):
    real_entities, real_status = kwe_solver.solve(lang=lang, query=query)
    assert expected_entities == real_entities
    assert expected_status == real_status
