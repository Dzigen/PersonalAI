import pytest

import sys
sys.path.insert(0, "../../")
from src.utils import ReturnStatus
from src.parsers.query_parser import qa_custom_entities_parse_func

GOOD_RESPONSE = "a | b | d"
BAD_RESPONSE = ... # TODO

@pytest.mark.parametrize("raw_response, expected_triplets, expected_status", [
    (GOOD_RESPONSE, ['a', 'b', 'd'], ReturnStatus.success)
])
def test_entities_parse_func(raw_response, expected_triplets, expected_status):
    triplets, status = qa_custom_entities_parse_func(raw_response)
    assert status == expected_status
    assert triplets == expected_triplets

def test_kw_formate():
    pass

def test_kw_parse():
    pass

def test_kw_preprocess():
    pass
