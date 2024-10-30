import pytest

import sys
sys.path.insert(0, "../../")
from src.utils import detect_lang, ReturnStatus
from src.parsers.memory_extraction import mem_custom_triplet_parse_func

GOOD_RESPONSE = 'a, b, c; d, e, f'
BAD_RESPONSE = 'a, b; , , '

@pytest.mark.parametrize("raw_response, expected_triplets, expected_status", [
    (GOOD_RESPONSE, [('a', 'b', 'c'), ('d', 'e', 'f')], ReturnStatus.success),
    (BAD_RESPONSE, [], ReturnStatus.bad_format)
])
def test_triplet_parse_func(raw_response, expected_triplets, expected_status):
    triplets, status = mem_custom_triplet_parse_func(raw_response)
    assert status == expected_status
    assert triplets == expected_triplets
