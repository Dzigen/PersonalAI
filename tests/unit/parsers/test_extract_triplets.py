import pytest
from typing import Dict, List, Tuple

import sys
sys.path.insert(0, "../../")
from src.utils import detect_lang, ReturnStatus, Triplet

from src.parsers.memorize_pipeline.extractor.triplet_extraction import\
      etriplets_custom_formate, etriplets_custom_parse,\
          etriplets_custom_postprocess

GOOD_RESPONSE = 'a, b, c; d, e, f'
BAD_RESPONSE = 'a, b; , , '

@pytest.mark.parametrize("text, expected_output, exception", [
    # пустая строка
    # непустая строка
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
    # валидный формат (один триплет)
    # валидный формат (несколько триплетов)
    # невалидный формат (;)
    # невалидный формат (,)
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


@pytest.mark.parametrize("parsed_response, rel_prop, node_prop, expected_output, exception", [
    # пустой rel_prop
    # пустой node_prop
    # пустая subj-строка
    # пустая obj-строка
    # путся rel-строка
    # один валидный триплет
    # несколько валидных триплетов
])
def test_custom_postprocess(parsed_response: List[Tuple[str, str, str]], rel_prop: Dict[str, object],
                            node_prop: Dict[str, object], expected_output: List[Triplet], exception: bool):
    try:
        triplets = etriplets_custom_postprocess(parsed_response)
    except Exception:
        assert exception
    else:
        assert not exception

    if not exception:
        assert expected_output == triplets
