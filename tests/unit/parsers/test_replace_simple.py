import pytest
from typing import Dict, Set, List

import sys
sys.path.insert(0, "../../")
from src.utils import ReturnStatus, Triplet

from src.parsers.memorize_pipeline.updator.replace_simple_triplets import \
      rs_custom_formate, rs_custom_parse, rs_custom_postprocess

from cases import VALID_SIMPLE_TRIPLET1, VALID_SIMPLE_TRIPLET2, VALID_SIMPLE_TRIPLET3,\
      REPLACE_SIMPLE_2AND3, REPLACE_SIMPLE_1, REPLACE_SIMPLE_2

@pytest.mark.parametrize("base_triplet, incident_triplets, expected_output, exception", [
    # 1. корректные base_triplet и incident_triplets (несколько)
    (VALID_SIMPLE_TRIPLET1, [VALID_SIMPLE_TRIPLET2, VALID_SIMPLE_TRIPLET3],
     {'ex_triplets': REPLACE_SIMPLE_2AND3, 'new_triplets': REPLACE_SIMPLE_1}, False),
    # 2. корректные base_triplet и incident_triplets (один)
    (VALID_SIMPLE_TRIPLET1, [VALID_SIMPLE_TRIPLET2],
     {'ex_triplets': REPLACE_SIMPLE_2, 'new_triplets': REPLACE_SIMPLE_1}, False),
    # 3. корректный base_triplet и  пустой incident_triplets
    (VALID_SIMPLE_TRIPLET1, [], None, True),
])
def test_custom_foramte(base_triplet: Triplet, incident_triplets: List[Triplet],
                        expected_output: Dict[str, str], exception: bool):
    try:
        real_output = rs_custom_formate(base_triplet, incident_triplets)
    except Exception:
        assert exception
    else:
        assert not exception

    if not exception:
        assert expected_output.keys() == real_output.keys()
        for expected_key in expected_output.keys():
            assert expected_output[expected_key] == real_output[expected_key]

from cases import REPLACE_SIMPLE_RAW_RESPONSE1, REPLACE_SIMPLE_RAW_RESPONSE2,\
      REPLACE_SIMPLE_RAW_RESPONSE3, REPLACE_SIMPLE_RAW_RESPONSE4,\
          REPLACE_SIMPLE_RAW_RESPONSE5, REPLACE_SIMPLE_RAW_RESPONSE6,\
          REPLACE_SIMPLE_RAW_RESPONSE7, REPLACE_SIMPLE_RAW_RESPONSE8

from cases import REPLACE_SIMPLE_PARSE_OUTPUT1, REPLACE_SIMPLE_PARSE_OUTPUT2

@pytest.mark.parametrize("raw_response, expected_output, exception", [
    # 1. один сопоставленный тезис
    (REPLACE_SIMPLE_RAW_RESPONSE1, REPLACE_SIMPLE_PARSE_OUTPUT1, False),
    # 2. несколько сопоставленных тезисов
    (REPLACE_SIMPLE_RAW_RESPONSE2, REPLACE_SIMPLE_PARSE_OUTPUT2, False),
    # 3. сопоставленные тезисы отсутствуют
    ("[]", dict(), False),
    # 4. невалидный response
    # 4.1. отсутствует стрелка
    (REPLACE_SIMPLE_RAW_RESPONSE3, None, True),
    # 4.2 отсутствуют скобки
    (REPLACE_SIMPLE_RAW_RESPONSE4, None, True),
    # 4.3 отсутствуют кавычки
    (REPLACE_SIMPLE_RAW_RESPONSE5, None, True),
    # 4.4 присутствуте специальный символ в тезисе
    # 4.4.1 стрелка
    (REPLACE_SIMPLE_RAW_RESPONSE6, None, True),
    # 4.4.2 скобки
    (REPLACE_SIMPLE_RAW_RESPONSE7, None, True),
    # 4.4.3 кавычки
    (REPLACE_SIMPLE_RAW_RESPONSE8, None, True)
])
def test_custom_parse(raw_response: str, expected_output: Dict[str, Set[str]],
                      exception: bool):
    try:
        real_output = rs_custom_parse(raw_response)
    except Exception:
        assert exception
    else:
        assert not exception

    if not exception:
        assert expected_output.keys() == real_output.keys()
        for expected_key in expected_output.keys():
            assert expected_output[expected_key] == real_output[expected_key]

from cases import VALID_SIMPLE_TRIPLET4, VALID_SIMPLE_TRIPLET5, VALID_SIMPLE_TRIPLET6

@pytest.mark.parametrize("parsed_response, base_triplet, incident_triplets, expected_output, exception", [
    # 1. разобранный new-triplet = base_triplet и разобранные existing-triplets содержатся в incident_triplets
    (REPLACE_SIMPLE_PARSE_OUTPUT2, VALID_SIMPLE_TRIPLET4, [VALID_SIMPLE_TRIPLET5, VALID_SIMPLE_TRIPLET6],
      [VALID_SIMPLE_TRIPLET5.id, VALID_SIMPLE_TRIPLET6.id], False),
    # 2. разобранный new-triplet != base_triplet
    (REPLACE_SIMPLE_PARSE_OUTPUT2, VALID_SIMPLE_TRIPLET5, [VALID_SIMPLE_TRIPLET6],
     [], False),
    # 3. разобранный new-triplet = base_triplet, но часть разобранных existing-triplets не содержится в incident_triplets
    (REPLACE_SIMPLE_PARSE_OUTPUT2, VALID_SIMPLE_TRIPLET4, [VALID_SIMPLE_TRIPLET5],
     [VALID_SIMPLE_TRIPLET5.id], False)
])
def test_custom_postprocess(parsed_response: Dict[str, Set[str]], base_triplet: Triplet,
                            incident_triplets: List[Triplet], expected_output: List[str], exception: bool):
    try:
        real_output = rs_custom_postprocess(
            parsed_response, base_triplet, incident_triplets)
    except Exception:
        assert exception
    else:
        assert not exception

    if not exception:
        assert expected_output == real_output
