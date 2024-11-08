import pytest
from chromadb.errors import ChromaError

import sys
sys.path.insert(0, "../../")

from cases import VECTORDB_CREAT_TEST_CASES, VECTORDB_DELETE_TEST_CASES, \
    VECTORDB_READ_TEST_CASES, VECTORDB_RETRIEVE_TEST_CASES, \
    VECTORDV_COUNT_TEST_CASES, VECTORDB_EXIST_TEST_CASES, \
    VECTORDB_CLEAR_TEST_CASES

@pytest.mark.parametrize("input, expected", VECTORDB_CREAT_TEST_CASES)
def test_create(input, expected, chromadb_conn):

    chromadb_conn.clear()
    try:
        for inp in input:
            chromadb_conn.create(inp)
    except (ChromaError, ValueError) as e:
        assert expected['exception']

    assert chromadb_conn.count_items() == expected['db_size']

@pytest.mark.parametrize("instances, input, expected", VECTORDB_DELETE_TEST_CASES)
def test_delete(instances, input, expected, chromadb_conn):
    pass

@pytest.mark.parametrize("input, expected", VECTORDB_READ_TEST_CASES)
def test_read(instances, input, expected, chromadb_conn):
    pass

@pytest.mark.parametrize("input, expected", VECTORDB_RETRIEVE_TEST_CASES)
def test_retrieve(instances, input, expected, chromadb_conn):
    pass

@pytest.mark.parametrize("input, expected", VECTORDV_COUNT_TEST_CASES)
def test_count_items(input, expected, chromadb_conn):
    pass

@pytest.mark.parametrize("input, expected", VECTORDB_EXIST_TEST_CASES)
def test_item_exist(instances, input, expected, chromadb_conn):
    pass

@pytest.mark.parametrize("input, expected", VECTORDB_CLEAR_TEST_CASES)
def test_clear(instances, expected, chromadb_conn):
    pass
