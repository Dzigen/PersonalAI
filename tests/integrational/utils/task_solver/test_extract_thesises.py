import pytest

import sys
sys.path.insert(0, "../../")

from src.utils import ReturnStatus, Triplet
from typing import List, Dict

@pytest.mark.parametrize("lang, text, node_prop, expected_thesises, expected_status", [
    # TODO
])
def test_extract_thesises(ethesises_solver, lang: str, text: str, node_prop: Dict[str, object],
                          expected_thesises: List[Triplet], expected_status: ReturnStatus):
    real_thesises, real_status = ethesises_solver.solve(lang, text=text, node_prop=node_prop)
    assert expected_thesises == real_thesises
    assert expected_status == real_status
