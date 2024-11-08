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
        print(str(e))
        assert expected['exception']

    assert chromadb_conn.count_items() == expected['db_size']

@pytest.mark.parametrize("instances, input, expected", VECTORDB_DELETE_TEST_CASES)
def test_delete(instances, input, expected, chromadb_conn):
    chromadb_conn.clear()
    chromadb_conn.create(instances)

    try:
        chromadb_conn.delete(input)
    except Exception as e:
        print(str(e))
        assert expected['exception']

    assert chromadb_conn.count_items() == expected['db_size']

@pytest.mark.parametrize("instances, input, expected", VECTORDB_READ_TEST_CASES)
def test_read(instances, input, expected, chromadb_conn):
    chromadb_conn.clear()
    chromadb_conn.create(instances)

    try:
        output = chromadb_conn.read(input)
    except Exception as e:
        print(str(e))
        assert expected['exception']

    if not expected['exception']:
        assert list(map(lambda item: item.id, output)) == expected['output_ids']

@pytest.mark.parametrize("instances, queries, n_results, expected", VECTORDB_RETRIEVE_TEST_CASES)
def test_retrieve(instances, queries, n_results, expected, chromadb_conn):
    chromadb_conn.clear()
    chromadb_conn.create(instances)

    try:
        output = chromadb_conn.retrieve(queries, n_results=n_results)
    except Exception as e:
        print(str(e))
        assert expected['exception']

    if not expected['exception']:
        for query_output in output:
            assert expected['output_size'] == len(query_output)

@pytest.mark.parametrize("instances, expected", VECTORDV_COUNT_TEST_CASES)
def test_count_items(instances, expected, chromadb_conn):
    chromadb_conn.clear()
    chromadb_conn.create(instances)

    assert chromadb_conn.count_items() == expected

@pytest.mark.parametrize("instances, input, expected", VECTORDB_EXIST_TEST_CASES)
def test_item_exist(instances, input, expected, chromadb_conn):
    chromadb_conn.clear()
    chromadb_conn.create(instances)

    try:
        real = chromadb_conn.item_exist(input)
    except Exception as e:
        print(str(e))
        assert expected['exception']

    if not expected['exception']:
        assert real == expected['exist']

@pytest.mark.parametrize("instances", VECTORDB_CLEAR_TEST_CASES)
def test_clear(instances, chromadb_conn):
    chromadb_conn.clear()
    chromadb_conn.create(instances)

    assert chromadb_conn.count_items() == len(instances)
    chromadb_conn.clear()
    assert chromadb_conn.count_items() == 0
