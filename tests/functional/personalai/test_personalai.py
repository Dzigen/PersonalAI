import pytest
from typing import List, Dict
from tqdm import tqdm
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
sys.path.insert(0, PROJECT_BASE_DIR)

from src import PersonalAI
from .cases import POPULATED_QUERIES_TEST_CASES

@pytest.mark.parametrize("query, personal_ai", POPULATED_QUERIES_TEST_CASES, indirect=['personal_ai'])
def test_personalai(query: str, personal_ai: PersonalAI):
    _, info = personal_ai.answer_question(query)
    assert info.status.value == 0
