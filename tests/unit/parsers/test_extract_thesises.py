import pytest
from typing import Dict, List, Set, Tuple

import sys
sys.path.insert(0, "../../")
from src.utils.data_structs import Triplet
from src.parsers.memorize_pipeline.extractor.thesis_extraction import\
      ethesises_custom_formate, ethesises_custom_parse,\
          ethesises_custom_postprocess

@pytest.mark.parametrize("text, expected_output, exception", [
    # пустая строка
    ("", None, True),
    # непустая строка
    ("simple text", {'text': 'simple text'}, False)
])
def test_custom_foramte(text: str, expected_output: Dict[str, str], exception: bool):
    try:
        formated_output = ethesises_custom_formate(text)
    except Exception:
        assert exception
    else:
        assert not exception

    if not exception:
        assert expected_output.keys() == formated_output.keys()
        for expected_key in expected_output.keys():
            assert expected_output[expected_key] == formated_output[expected_key]


GOOD_RESPONSE1 = "a; ['b', 'c']."
GOOD_RESPONSE2 = "a; ['b', 'c']. d; ['e', 'f']."
BAD_RESPONSE1 = "a ['b', 'c']. d ['e', 'f']."
BAD_RESPONSE2 = "a; ['b' 'c']. d; ['e' 'f']."
BAD_RESPONSE3 = "a; 'b', 'c'. d; 'e', 'f'."
BAD_RESPONSE4 = "a; 'b', 'c'. d; 'e', 'f'."

@pytest.mark.parametrize("raw_response, expected_output, exception", [
    # пустая строка
    ("",None, True),
    # валидный формат (один триплет)
    (GOOD_RESPONSE1, [('a', ['b','c'])], False),
    # валидный формат (несколько триплетов)
    (GOOD_RESPONSE2, [('a',['b','c']), ('d',['e','f'])], False),
    # невалидный формат (;)
    (BAD_RESPONSE1, None, True),
    # невалидный формат (,)
    (BAD_RESPONSE2, None, True),
    # невалидный формат (скобки)
    (BAD_RESPONSE3, None, True),
    # невалидный формат (кавычки)
    (BAD_RESPONSE4, None, True)
])
def test_custom_parse(raw_response: str, expected_output: List[Tuple[str, str, str]],
                      exception: bool):
    try:
        parsed_output = ethesises_custom_parse(raw_response)
    except Exception:
        assert exception
    else:
        assert not exception

    if not exception:
        assert expected_output == parsed_output


from cases import VALID_HYPER_TRIPLET1, VALID_HYPER_TRIPLET1_2,\
      VALID_HYPER_TRIPLET7, VALID_HYPER_TRIPLET8

@pytest.mark.parametrize("parsed_response, rel_prop, node_prop, expected_output, exception", [
    # пустой rel_prop
    ([('rty',['qwe'])], dict(), {'k1': 'v1'}, [VALID_HYPER_TRIPLET7], False),
    # пустой node_prop
    ([('qsdcb',['qazxsw'])], {'k5': 'v5'}, dict(), [VALID_HYPER_TRIPLET8], False),
    # пустая thesis-строка
    ([('',['qwe', 'asd'])], dict(), dict(), None, True),
    # пустая entity-строка
    ([('rty',['', 'asd'])], dict(), dict(), None, True),
    # несколько валидных тезисов
    ([('rty',['qwe', 'asd'])], {'k5': 'v5'}, {'k1': 'v1'}, [VALID_HYPER_TRIPLET1, VALID_HYPER_TRIPLET1_2], False)
])
def test_custom_postprocess(parsed_response: List[Tuple[str, str, str]], rel_prop: Dict[str, object],
                            node_prop: Dict[str, object], expected_output: List[Triplet], exception: bool):
    try:
        triplets = ethesises_custom_postprocess(parsed_response, node_prop, rel_prop)
    except Exception:
        assert exception
    else:
        assert not exception

    if not exception:
        for t1, t2 in zip(triplets, expected_output):
            print(t1.id, t2.id)
            print(t1.start_node.id, t2.start_node.id)
            print(t1.relation.id, t2.relation.id)
            print(t1.end_node.id, t2.end_node.id)

            print(t1)
            print(t2)

        assert expected_output == triplets
