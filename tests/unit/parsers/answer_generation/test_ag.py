import sys
import pytest
from typing import List, Dict
from collections import defaultdict

# TO CHANGE
PROJECT_BASE_DIR = '../'
sys.path.insert(0, PROJECT_BASE_DIR)
from src.utils import Triplet

from v1_tcases import AG_V1_TEST_CASES
from v2_tcases import AG_V2_TEST_CASES
from general_tcases import AG_FORMATE_TEST_CASES, AG_POSTPROCESS_TEST_CASES


#
AVAILABLE_PARSERS_METHODS = ['formate', 'parse', 'postprocess']
AVAILABLE_AG_VERSIONS = {
    'v1': AG_V1_TEST_CASES,
    'v2': AG_V2_TEST_CASES
}

AG_AGGREGATED_TEST_CASES = defaultdict(list)
for pmethod_name in AVAILABLE_PARSERS_METHODS:
    for v_key, v_tcases in AVAILABLE_AG_VERSIONS:
        AG_AGGREGATED_TEST_CASES[pmethod_name].append(AVAILABLE_AG_VERSIONS[v_key][pmethod_name] + [v_key])

@pytest.mark.parametrize("query, context_triplets, expected_output, exception, ag_tconfig", AG_FORMATE_TEST_CASES, indirect=['ag_tconfig'])
def test_qa_custom_formate(query: str, context_triplets: List[Triplet],
                           expected_output: Dict[str, str], exception: bool, ag_tconfig: Dict[str, object]):
    try:
        formated_output = ag_tconfig['custom_formate'](query, context_triplets)
    except Exception:
        assert exception
    else:
        assert not exception

    if not exception:
        assert expected_output.keys() == formated_output.keys()
        for expected_key in expected_output.keys():
            assert expected_output[expected_key] == formated_output[expected_key]


@pytest.mark.parametrize("raw_response, lang, expected_output, exception, ag_tconfig", AG_AGGREGATED_TEST_CASES['parse'], indirect=['ag_tconfig'])
def test_qa_parse(raw_response: str, lang: str, expected_output: Dict[str, str],
                  exception: bool, ag_tconfig: Dict[str, object]):
    try:
        parsed_output = ag_tconfig['custom_formate'][lang].parse_answer_func(raw_response)
    except Exception:
        assert exception
    else:
        assert not exception

    if not exception:
        assert parsed_output == expected_output


@pytest.mark.parametrize("parsed_response, lang, expected_output, exception, ag_tconfig", AG_AGGREGATED_TEST_CASES['postprocess'], indirect=['ag_tconfig'])
def test_qa_postprocess(parsed_response: str, lang: str, expected_output: str,
                        exception: bool, ag_tconfig: Dict[str, object]):
    try:
        real_answer = ag_tconfig['custom_formate'][lang].postprocess_answer_func(parsed_response)
    except Exception:
        assert exception
    else:
        assert not exception

    if not exception:
        assert real_answer == expected_output
