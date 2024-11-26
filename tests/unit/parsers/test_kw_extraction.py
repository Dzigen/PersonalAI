import pytest
from typing import Dict, List

import sys
sys.path.insert(0, "../../")
from src.utils import ReturnStatus
from src.parsers.qa_pipeline.query_parser.kw_extraction import kwe_custom_formate, kwe_custom_parse, kwe_custom_postprocess

@pytest.mark.parametrize("query, expected_output, exception", [
    # непустая строка
    ("simple query", {'text': 'simple query'}, False),
    # пустая строка
    ("", None, True)
])
def test_custom_formate(query: str, expected_output: Dict[str, str], exception: bool):
    try:
         formated_output = kwe_custom_formate(query)
    except Exception:
        assert exception
    else:
        assert not exception

    if not exception:
        assert expected_output.keys() == formated_output.keys()
        for expected_key in expected_output.keys():
            assert expected_output[expected_key] == formated_output[expected_key]


@pytest.mark.parametrize("raw_response, expected_output, exception", [
    # пустая строк
    (' .', [], False),
    # одна сущность
    ('asd.', ['asd'], False),
    # несколько сущностей
    ('asd | qwe | zxc.', ['asd', 'qwe', 'zxc'], False)
])
def test_kw_parse(raw_response: str, expected_output: List[str], exception: bool):
    try:
         parsed_output = kwe_custom_parse(raw_response)
    except Exception:
        assert exception
    else:
        assert not exception

    if not exception:
        assert expected_output == parsed_output

@pytest.mark.parametrize("parsed_output, expected_output, exception", [
    # Пустой список
    ([], None, True),
    # Непустой список
    (['asd', 'zxc'], ['asd', 'zxc'], False)
])
def test_kw_postprocess(parsed_output: List[str], expected_output: List[str], exception: bool):
    try:
         postprocessed_output = kwe_custom_postprocess(parsed_output)
    except Exception:
        assert exception
    else:
        assert not exception

    if not exception:
        assert expected_output == postprocessed_output
