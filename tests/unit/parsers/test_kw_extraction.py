import pytest
from typing import Dict, List

import sys
sys.path.insert(0, "../../")
from src.utils import ReturnStatus
from src.parsers.qa_pipeline.query_parser.kw_extraction import kwe_custom_formate, kwe_custom_parse, kwe_custom_postprocess


GOOD_RESPONSE = "a | b | d"
BAD_RESPONSE = ... # TODO

@pytest.mark.parametrize("query, expected_output, exception", [
    ("simple query", {'text': 'simple query'}, False)
])
def test_custom_formate(query: str, expected_output: Dict[str, str], exception: bool):
    try:
         real_output = kwe_custom_formate(query)
    except Exception:
        assert exception
    else:
        assert not exception

    if not exception:
        assert expected_output == real_output

@pytest.mark.parametrize("raw_response, parsed_output, exception", [
    (GOOD_RESPONSE, ['a', 'b', 'd'], ReturnStatus.success)
])
def test_kw_parse(raw_response: str, parsed_output: List[str], exception: bool):
    pass

def test_kw_preprocess(parsed_output: List[str], expected_output: List[str], exception: bool):
    pass
