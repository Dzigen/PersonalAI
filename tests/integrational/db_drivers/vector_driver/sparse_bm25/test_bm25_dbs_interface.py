import pytest
from chromadb.errors import ChromaError
from typing import Dict, List
#from pymilvus.exceptions import DataNotMatchException, ParamError, MilvusException
import sys
sys.path.insert(0, "../")

from .cases import BM25_POPULATED_CREATE_TEST_CASES, BM25_POPULATED_DELETE_TEST_CASES, \
    BM25_POPULATED_READ_TEST_CASES, BM25_POPULATED_RETRIEVE_TEST_CASES, \
    BM25_POPULATED_COUNT_TEST_CASES, BM25_POPULATED_EXIST_TEST_CASES, \
    BM25_POPULATED_CLEAR_TEST_CASES, BM25_POPULATED_UPSERT_TEST_CASES, \
        BM25_POPULATED_IS_OPEN_TEST_CASES
from src.db_drivers.vector_driver.utils import AbstractVectorDatabaseConnection
from src.db_drivers.vector_driver import VectorDBInstance


@pytest.mark.parametrize("input, expected, vectordb_sparsebm25_conn",
                         BM25_POPULATED_CREATE_TEST_CASES,
                         indirect=['vectordb_sparsebm25_conn'])
def test_create(input: List[List[VectorDBInstance]], expected: Dict[str, object],
                vectordb_sparsebm25_conn: AbstractVectorDatabaseConnection):
    vectordb_sparsebm25_conn.clear()

    try:
        for inp in input:
            vectordb_sparsebm25_conn.create(inp)
    except (ChromaError, ValueError, AssertionError) as e:
        print(str(e))
        assert expected['exception']
    else:
        assert not expected['exception']
        for item in inp:
            assert vectordb_sparsebm25_conn.item_exist(item.id)

    assert vectordb_sparsebm25_conn.count_items() == expected['db_size']


@pytest.mark.parametrize("instances, input, expected, vectordb_sparsebm25_conn",
                         BM25_POPULATED_READ_TEST_CASES, indirect=['vectordb_sparsebm25_conn'])
def test_read(instances: List[VectorDBInstance], input: List[VectorDBInstance], expected: Dict[str, object],
              vectordb_sparsebm25_conn: AbstractVectorDatabaseConnection):
    vectordb_sparsebm25_conn.clear()
    vectordb_sparsebm25_conn.create(instances)

    try:
        output = vectordb_sparsebm25_conn.read(input)
    except ValueError as e:
        print(str(e))
        assert expected['exception']
    else:
        assert not expected['exception']

    if not expected['exception']:
        assert list(map(lambda item: item.id, output)
                    ) == expected['output_ids']


@pytest.mark.parametrize("init_instance, new_instances, exception, expected_count, vectordb_sparsebm25_conn",
                         BM25_POPULATED_UPSERT_TEST_CASES, indirect=['vectordb_sparsebm25_conn'])
def test_upsert(init_instance: List[VectorDBInstance], new_instances: Dict[str, VectorDBInstance],
                exception: bool, expected_count: int, vectordb_sparsebm25_conn: AbstractVectorDatabaseConnection):
    vectordb_sparsebm25_conn.clear()
    assert vectordb_sparsebm25_conn.count_items() < 1
    vectordb_sparsebm25_conn.create(init_instance)
    assert vectordb_sparsebm25_conn.count_items() == len(init_instance)

    try:
        vectordb_sparsebm25_conn.upsert(list(new_instances.values()))
    except ValueError as e:
        print(str(e))
        assert exception
    else:
        assert not exception

        real_contents = vectordb_sparsebm25_conn.read(list(new_instances.keys()))
        assert len(real_contents) == len(new_instances)
        for item in real_contents:
            assert item.document == new_instances[item.id].document
            assert item.embedding is None
            assert item.metadata == new_instances[item.id].metadata

        real_count = vectordb_sparsebm25_conn.count_items()
        assert real_count == expected_count


@pytest.mark.parametrize("instances, delete_ids, expected, vectordb_sparsebm25_conn",
                         BM25_POPULATED_DELETE_TEST_CASES, indirect=['vectordb_sparsebm25_conn'])
def test_delete(instances, delete_ids, expected, vectordb_sparsebm25_conn: AbstractVectorDatabaseConnection):
    vectordb_sparsebm25_conn.clear()
    vectordb_sparsebm25_conn.create(instances)

    try:
        vectordb_sparsebm25_conn.delete(delete_ids)
    except ValueError as e:
        print(str(e))
        assert expected['exception']
    else:
        assert not expected['exception']
        for d_id in delete_ids:
            assert not vectordb_sparsebm25_conn.item_exist(d_id)

        assert vectordb_sparsebm25_conn.count_items() == expected['db_size']


@pytest.mark.parametrize("instances, queries, n_results, subset_ids, expected, vectordb_sparsebm25_conn",
                         BM25_POPULATED_RETRIEVE_TEST_CASES, indirect=['vectordb_sparsebm25_conn'])
def test_retrieve(instances: List[VectorDBInstance], queries: List[str], n_results: int, subset_ids: List[str],
                  expected: Dict[str, object], vectordb_sparsebm25_conn: AbstractVectorDatabaseConnection):
    vectordb_sparsebm25_conn.clear()
    vectordb_sparsebm25_conn.create(instances)
    for item in instances:
        assert vectordb_sparsebm25_conn.item_exist(item.id)
    assert vectordb_sparsebm25_conn.count_items() == len(instances)

    try:
        output = vectordb_sparsebm25_conn.retrieve(
            queries, n_results=n_results, subset_ids=subset_ids)
    except (ValueError, AssertionError) as e:
        print(str(e))
        assert expected['exception']
    else:
        assert not expected['exception']

        for query_output in output:
            assert expected['output_size'] == len(query_output)

            real_scores = list(map(lambda item: item[0], query_output))
            sorted_scores = sorted(real_scores, reverse=True)
            assert real_scores == sorted_scores

            for real_score in real_scores:
                assert real_score < 1.0


@pytest.mark.parametrize("instances, expected, vectordb_sparsebm25_conn",
                         BM25_POPULATED_COUNT_TEST_CASES,
                         indirect=['vectordb_sparsebm25_conn'])
def test_count_items(instances: List[VectorDBInstance], expected: Dict[str, int],
                     vectordb_sparsebm25_conn: AbstractVectorDatabaseConnection):
    vectordb_sparsebm25_conn.clear()
    assert vectordb_sparsebm25_conn.count_items() == 0

    vectordb_sparsebm25_conn.create(instances)
    assert vectordb_sparsebm25_conn.count_items() == expected


@pytest.mark.parametrize("instances, input_id, expected, vectordb_sparsebm25_conn",
                         BM25_POPULATED_EXIST_TEST_CASES, indirect=['vectordb_sparsebm25_conn'])
def test_item_exist(instances: List[VectorDBInstance], input_id: object, expected: Dict[str, object],
                    vectordb_sparsebm25_conn: AbstractVectorDatabaseConnection):
    vectordb_sparsebm25_conn.clear()
    vectordb_sparsebm25_conn.create(instances)

    try:
        real = vectordb_sparsebm25_conn.item_exist(input_id)
    except ValueError as e:
        print(str(e))
        assert expected['exception']
    else:
        assert not expected['exception']
        assert real == expected['exist']


@pytest.mark.parametrize("instances, vectordb_sparsebm25_conn", BM25_POPULATED_CLEAR_TEST_CASES, indirect=['vectordb_sparsebm25_conn'])
def test_clear(instances: List[VectorDBInstance], vectordb_sparsebm25_conn: AbstractVectorDatabaseConnection):
    vectordb_sparsebm25_conn.clear()
    assert vectordb_sparsebm25_conn.count_items() == 0

    vectordb_sparsebm25_conn.create(instances)
    assert vectordb_sparsebm25_conn.count_items() == len(instances)

    vectordb_sparsebm25_conn.clear()
    assert vectordb_sparsebm25_conn.count_items() == 0

@pytest.mark.parametrize("conn_sequence, vectordb_sparsebm25_conn", BM25_POPULATED_IS_OPEN_TEST_CASES, indirect=['vectordb_sparsebm25_conn'])
def test_is_open(conn_sequence: List[str], vectordb_sparsebm25_conn: AbstractVectorDatabaseConnection):
    assert vectordb_sparsebm25_conn.is_open()

    for conn_kw in conn_sequence:
        if conn_kw == 'open':
            vectordb_sparsebm25_conn.open_connection()
            assert vectordb_sparsebm25_conn.is_open()
        elif conn_kw == 'close':
            vectordb_sparsebm25_conn.close_connection()
            assert not vectordb_sparsebm25_conn.is_open()
        else:
            raise ValueError

    vectordb_sparsebm25_conn.open_connection()
    assert vectordb_sparsebm25_conn.is_open()