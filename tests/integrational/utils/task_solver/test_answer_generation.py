import pytest

import sys
sys.path.insert(0, "../../")

from src.utils import ReturnStatus, Triplet
from typing import List, Dict

@pytest.mark.parametrize("lang, query, context_triplets, expected_answer, expected_status", [
    # TODO
])
def test_answer_generation(ag_solver, lang: str, query: str, context_triplets: List[Triplet],
                           expected_answer: str, expected_status: ReturnStatus):
    real_answer, real_status = ag_solver.solve(lang, query=query, context_tripelets=context_triplets)
    assert expected_answer == real_answer
    assert expected_status == real_status
