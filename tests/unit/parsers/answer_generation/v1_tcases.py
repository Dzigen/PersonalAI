import sys

# TO CHANGE
PROJECT_BASE_DIR = '../'
sys.path.insert(0, PROJECT_BASE_DIR)
from src.utils import Triplet, TripletCreator

AG_ONE_CONTEXT = f'- {TripletCreator.stringify(VALID_SIMPLE_TRIPLET1)[1]}'
AG_SEVERAL_CONTEXTS = '\n'.join(list(map(lambda triplet: f'- {TripletCreator.stringify(triplet)[1]}', [VALID_SIMPLE_TRIPLET1, VALID_HYPER_TRIPLET1])))

EN_GOOD_RESPONSE1 = 'Chain of thought 3: bla bla bla\nFinal answer 3: simple answer'
EN_BAD_RESPONSE1 = 'Chain of thought 3: bla bla bla\nFinal answer 3: '
EN_BAD_RESPONSE2 = 'Chain of thought 3: bla bla bla\nFInaL aNsWer: simple answer'



# "raw_response, lang, expected_output, exception"
AG_PARSE_V1_TEST_CASES = [
    # пустая строка
    ('', None, True),
    # валидный формат + есть ответ\
    (EN_GOOD_RESPONSE1, 'simple answer', False),
    # валидный формат + пустой ответ
    (EN_BAD_RESPONSE1, None, True),
    # изменённый регистр формата
    (EN_BAD_RESPONSE2, 'simple answer', False)
]
