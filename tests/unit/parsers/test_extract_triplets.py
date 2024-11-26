import pytest
from typing import Dict, List, Tuple

import sys
sys.path.insert(0, "../../")
from src.utils import detect_lang, ReturnStatus, Triplet

from src.parsers.memorize_pipeline.extractor.triplet_extraction import\
      etriplets_custom_formate, etriplets_custom_parse,\
          etriplets_custom_postprocess

GOOD_RESPONSE1 = 'a, b, c; d, e, f.'
GOOD_RESPONSE2 = 'a, b, c.'
BAD_RESPONSE1 = 'a, b, c; d e f.'
BAD_RESPONSE2 = 'a, b, c, d, e, f.'

@pytest.mark.parametrize("text, expected_output, exception", [
    # пустая строка
    ("", None, True),
    # непустая строка
    ("simple text", {'text': 'simple text'}, False)
])
def test_custom_foramte(text: str, expected_output: Dict[str, str], exception: bool):
    try:
        formated_output = etriplets_custom_formate(text)
    except Exception:
        assert exception
    else:
        assert not exception

    if not exception:
        assert expected_output.keys() == formated_output.keys()
        for expected_key in expected_output.keys():
            assert expected_output[expected_key] == formated_output[expected_key]


@pytest.mark.parametrize("raw_response, expected_output, exception", [
    # пустая строка
    ("",None, True),
    # валидный формат (один триплет)
    (GOOD_RESPONSE2, [('a','b','c')], False),
    # валидный формат (несколько триплетов)
    (GOOD_RESPONSE1, [('a','b','c'), ('d','e','f')], False),
    # невалидный формат (;)
    (BAD_RESPONSE1, None, True),
    # невалидный формат (,)
    (BAD_RESPONSE2, None, True)
])
def test_custom_parse(raw_response: str, expected_output: List[Tuple[str, str, str]],
                      exception: bool):
    try:
        parsed_output = etriplets_custom_parse(raw_response)
    except Exception:
        assert exception
    else:
        assert not exception

    if not exception:
        assert expected_output == parsed_output


from cases import VALID_SIMPLE_TRIPLET1, VALID_SIMPLE_TRIPLET2,\
      VALID_SIMPLE_TRIPLET7, VALID_SIMPLE_TRIPLET8

@pytest.mark.parametrize("parsed_response, rel_prop, node_prop, expected_output, exception", [
    # пустой rel_prop
    ([('qwe', 'rfvbgt', 'asd')], dict(), {'k1': 'v1'}, [VALID_SIMPLE_TRIPLET8], False),
    # пустой node_prop
    ([('qazxsw', 'zxc', 'qazxsw')], {'k3': 'v3'}, dict(), [VALID_SIMPLE_TRIPLET7], False),
    # пустая subj-строка
    ([('', 'zxc', 'asd')], dict(), dict(), None, True),
    # пустая obj-строка
    ([('qwe', 'zxc', '')], dict(), dict(), None, True),
    # путся rel-строка
    ([('qwe', '', 'asd')], dict(), dict(), None, True),
    # несколько валидных триплетов
    ([('qwe', 'zxc', 'asd'), ('asd', 'zxc', 'uio')], {'k3': 'v3'}, {'k1': 'v1'},
     [VALID_SIMPLE_TRIPLET1, VALID_SIMPLE_TRIPLET2], False)
])
def test_custom_postprocess(parsed_response: List[Tuple[str, str, str]], rel_prop: Dict[str, object],
                            node_prop: Dict[str, object], expected_output: List[Triplet], exception: bool):
    try:
        triplets = etriplets_custom_postprocess(parsed_response, node_prop, rel_prop)
    except Exception:
        assert exception
    else:
        assert not exception

    if not exception:
        for t1, t2 in zip(triplets, expected_output):
            print(t1.start_node)
            print(t2.start_node)
            print("===")
            print(t1.relation)
            print(t2.relation)
            print("===")
            print(t1.end_node)
            print(t2.end_node)
            print("===")

        assert expected_output == triplets
