import pytest
from chromadb.errors import ChromaError
from pymilvus.exceptions import DataNotMatchException, ParamError, MilvusException
import sys
sys.path.insert(0, "../")

from cases import VECTORDB_POPULATED_CREATE_TEST_CASES, VECTORDB_POPULATED_DELETE_TEST_CASES, \
    VECTORDB_POPULATED_READ_TEST_CASES, VECTORDB_POPULATED_RETRIEVE_TEST_CASES, \
    VECTORDB_POPULATED_COUNT_TEST_CASES, VECTORDB_POPULATED_EXIST_TEST_CASES, \
    VECTORDB_POPULATED_CLEAR_TEST_CASES

@pytest.mark.parametrize("input, expected, vectordb_conn", VECTORDB_POPULATED_CREATE_TEST_CASES, indirect=['vectordb_conn'])
def test_create(input, expected, vectordb_conn):
    vectordb_conn.clear()

    try:
        for inp in input:
            vectordb_conn.create(inp)
    except (ChromaError, ValueError, AssertionError, DataNotMatchException) as e:
        print(str(e))
        assert expected['exception']
    else:
        assert not expected['exception']
        for item in inp:
            assert vectordb_conn.item_exist(item.id)

    assert vectordb_conn.count_items() == expected['db_size']

@pytest.mark.parametrize("instances, input, expected, vectordb_conn", VECTORDB_POPULATED_READ_TEST_CASES, indirect=['vectordb_conn'])
def test_read(instances, input, expected, vectordb_conn):
    vectordb_conn.clear()
    vectordb_conn.create(instances)

    try:
        output = vectordb_conn.read(input)
    except ValueError as e:
        print(str(e))
        assert expected['exception']
    else:
        assert not expected['exception']

    if not expected['exception']:
        assert list(map(lambda item: item.id, output)) == expected['output_ids']

@pytest.mark.parametrize("instances, delete_ids, expected, vectordb_conn", VECTORDB_POPULATED_DELETE_TEST_CASES, indirect=['vectordb_conn'])
def test_delete(instances, delete_ids, expected, vectordb_conn):
    vectordb_conn.clear()
    vectordb_conn.create(instances)

    try:
        vectordb_conn.delete(delete_ids)
    except ValueError as e:
        print(str(e))
        assert expected['exception']
    else:
        assert not expected['exception']
        for d_id in delete_ids:
            assert not vectordb_conn.item_exist(d_id)

        assert vectordb_conn.count_items() == expected['db_size']

@pytest.mark.parametrize("instances, queries, n_results, subset_ids, expected, vectordb_conn", VECTORDB_POPULATED_RETRIEVE_TEST_CASES, indirect=['vectordb_conn'])
def test_retrieve(instances, queries, n_results, subset_ids, expected, vectordb_conn):
    vectordb_conn.clear()
    vectordb_conn.create(instances)
    for item in instances:
        assert vectordb_conn.item_exist(item.id)

    try:
        output = vectordb_conn.retrieve(queries, n_results=n_results, subset_ids=subset_ids)
    except (ValueError, AssertionError, ParamError, MilvusException) as e:
        print(str(e))
        assert expected['exception']
    else:
        assert not expected['exception']

        for query_output in output:
            assert expected['output_size'] == len(query_output)

@pytest.mark.parametrize("instances, expected, vectordb_conn", VECTORDB_POPULATED_COUNT_TEST_CASES, indirect=['vectordb_conn'])
def test_count_items(instances, expected, vectordb_conn):
    vectordb_conn.clear()
    vectordb_conn.create(instances)

    assert vectordb_conn.count_items() == expected

@pytest.mark.parametrize("instances, input_id, expected, vectordb_conn", VECTORDB_POPULATED_EXIST_TEST_CASES, indirect=['vectordb_conn'])
def test_item_exist(instances, input_id, expected, vectordb_conn):
    vectordb_conn.clear()
    vectordb_conn.create(instances)

    try:
        real = vectordb_conn.item_exist(input_id)
    except ValueError as e:
        print(str(e))
        assert expected['exception']
    else:
        assert not expected['exception']
        assert real == expected['exist']

@pytest.mark.parametrize("instances, vectordb_conn", VECTORDB_POPULATED_CLEAR_TEST_CASES, indirect=['vectordb_conn'])
def test_clear(instances, vectordb_conn):
    vectordb_conn.clear()
    vectordb_conn.create(instances)

    assert vectordb_conn.count_items() == len(instances)
    vectordb_conn.clear()
    assert vectordb_conn.count_items() == 0
