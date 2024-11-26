import pytest
from typing import List, Dict

import sys
sys.path.insert(0, "../../")

from src.utils import Triplet, TripletCreator
from src.parsers.qa_pipeline.answer_generator.question_answering import \
      ag_custom_foramte, ag_custom_postprocess,\
      en_ag_custom_answer_parse, ru_ag_custom_answer_parse

from cases import VALID_HYPER_TRIPLET1, VALID_SIMPLE_TRIPLET1

AG_ONE_CONTEXT = f'- {TripletCreator.stringify(VALID_SIMPLE_TRIPLET1)[1]}'
AG_SEVERAL_CONTEXTS = '\n'.join(list(map(lambda triplet: f'- {TripletCreator.stringify(triplet)[1]}', [VALID_SIMPLE_TRIPLET1, VALID_HYPER_TRIPLET1])))

@pytest.mark.parametrize("query, context_triplets, expected_output, exception", [
    # пустая query-строка
    ('', [VALID_SIMPLE_TRIPLET1, VALID_HYPER_TRIPLET1], None, True),
    # путой context_triplet-список
    ('simple query', [], None, True),
    # один элемент в context_triplets-списке
    ('simple query', [VALID_SIMPLE_TRIPLET1],
     {'q': 'simple query', 'c': AG_ONE_CONTEXT}, False),
    # несколько элементов в context_triplets-списке
    ('simple query', [VALID_SIMPLE_TRIPLET1, VALID_HYPER_TRIPLET1],
     {'q': 'simple query', 'c': AG_SEVERAL_CONTEXTS}, False)
])
def test_qa_custom_formate(query: str, context_triplets: List[Triplet],
                           expected_output: Dict[str, str], exception: bool):
    try:
        formated_output = ag_custom_foramte(query, context_triplets)
    except Exception:
        assert exception
    else:
        assert not exception

    if not exception:
        assert formated_output == expected_output

EN_GOOD_RESPONSE1 = 'Chain of thought 3: bla bla bla\nFinal answer 3: simple answer'
EN_BAD_RESPONSE1 = 'Chain of thought 3: bla bla bla\nFinal answer 3: '
EN_BAD_RESPONSE2 = 'Chain of thought 3: bla bla bla\nFInaL aNsWer: simple answer'

@pytest.mark.parametrize("raw_response, expected_output, exception", [
    # пустая строка
    ('', None, True),
    # валидный формат + есть ответ\
    (EN_GOOD_RESPONSE1, 'simple answer', False),
    # валидный формат + пустой ответ
    (EN_BAD_RESPONSE1, None, True),
    # изменённый регистр формата
    (EN_BAD_RESPONSE2, 'simple answer', False)
])
def test_qa_en_parse(raw_response: str, expected_output: Dict[str, str], exception: bool):
    try:
        parsed_output = en_ag_custom_answer_parse(raw_response)
    except Exception:
        assert exception
    else:
        assert not exception

    if not exception:
        assert parsed_output == expected_output

RU_GOOD_RESPONSE1 = '{a}'

@pytest.mark.parametrize("raw_response, expected_output, exception", [
    # пустая строка
    ('', None, True),
    # валидный формат + есть ответ
    ('simple answer', 'simple answer', False),
])
def test_qa_ru_parse(raw_response: str, expected_output: Dict[str, str], exception: bool):
    try:
        parsed_output = ru_ag_custom_answer_parse(raw_response)
    except Exception:
        assert exception
    else:
        assert not exception

    if not exception:
        assert parsed_output == expected_output

@pytest.mark.parametrize("parsed_response, expected_output, exception", [
    # пустая строка
    ("", None, True),
    # непустая строка
    ("simple answer", "simple answer", False),
])
def test_qa_postprocess(parsed_response: str, expected_output: str, exception: bool):
    try:
        real_answer = ag_custom_postprocess(parsed_response)
    except Exception:
        assert exception
    else:
        assert not exception

    if not exception:
        assert real_answer == expected_output
