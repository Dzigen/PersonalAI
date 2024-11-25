import pytest

import sys
sys.path.insert(0, "../../")
from src.utils import detect_lang, ReturnStatus
from src.parsers.question_answering import qa_custom_answer_parse_func_en

GOOD_RESPONSE = 'bla bla bla\nFinal answer 3: answer'

@pytest.mark.parametrize("raw_response, expected_triplets, expected_status", [
    (GOOD_RESPONSE, 'answer', ReturnStatus.success)
])
def test_qa_en_parse_func(raw_response, expected_triplets, expected_status):
    triplets, status = qa_custom_answer_parse_func_en(raw_response)
    assert status == expected_status
    assert triplets == expected_triplets

import pytest

import sys
sys.path.insert(0, "../../")
from src.utils import detect_lang, ReturnStatus
from src.parsers.question_answering import qa_custom_answer_parse_func_ru

GOOD_RESPONSE = ... # TODO
BAD_RESPONSE = ... # TODO

@pytest.mark.parametrize("raw_response, expected_triplets, expected_status", [
    # TODO
])
def test_qa_ru_parse_func(raw_response, expected_triplets, expected_status):
    triplets, status = qa_custom_answer_parse_func_ru(raw_response)
    assert status == expected_status
    assert triplets == expected_triplets
