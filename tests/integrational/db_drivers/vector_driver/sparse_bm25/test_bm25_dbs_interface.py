import pytest
from chromadb.errors import ChromaError
from typing import Dict, List
from pymilvus.exceptions import DataNotMatchException, ParamError, MilvusException
import sys
sys.path.insert(0, "../")

from .cases import BM25_POPULATED_CREATE_TEST_CASES, BM25_POPULATED_DELETE_TEST_CASES, \
    BM25_POPULATED_READ_TEST_CASES, BM25_POPULATED_RETRIEVE_TEST_CASES, \
    BM25_POPULATED_COUNT_TEST_CASES, BM25_POPULATED_EXIST_TEST_CASES, \
    BM25_POPULATED_CLEAR_TEST_CASES, BM25_POPULATED_UPSERT_TEST_CASES
from src.db_drivers.vector_driver.utils import AbstractVectorDatabaseConnection
from src.db_drivers.vector_driver import VectorDBInstance


@pytest.mark.parametrize("input, expected, bm25_conn",
                         BM25_POPULATED_CREATE_TEST_CASES,
                         indirect=['bm25_conn'])
def test_create(input: List[List[VectorDBInstance]], expected: Dict[str, object],
                bm25_conn: AbstractVectorDatabaseConnection):
    bm25_conn.clear()

    try:
        for inp in input:
            bm25_conn.create(inp)
    except (ChromaError, ValueError, AssertionError, DataNotMatchException) as e:
        print(str(e))
        assert expected['exception']
    else:
        assert not expected['exception']
        for item in inp:
            assert bm25_conn.item_exist(item.id)

    assert bm25_conn.count_items() == expected['db_size']


@pytest.mark.parametrize("instances, input, expected, bm25_conn",
                         BM25_POPULATED_READ_TEST_CASES, indirect=['bm25_conn'])
def test_read(instances: List[VectorDBInstance], input: List[VectorDBInstance], expected: Dict[str, object],
              bm25_conn: AbstractVectorDatabaseConnection):
    bm25_conn.clear()
    bm25_conn.create(instances)

    try:
        output = bm25_conn.read(input)
    except ValueError as e:
        print(str(e))
        assert expected['exception']
    else:
        assert not expected['exception']

    if not expected['exception']:
        assert list(map(lambda item: item.id, output)
                    ) == expected['output_ids']


@pytest.mark.parametrize("init_instance, new_instances, exception, expected_count, bm25_conn",
                         BM25_POPULATED_UPSERT_TEST_CASES, indirect=['bm25_conn'])
def test_upsert(init_instance: List[VectorDBInstance], new_instances: Dict[str, VectorDBInstance],
                exception: bool, expected_count: int, bm25_conn: AbstractVectorDatabaseConnection):
    bm25_conn.clear()
    assert bm25_conn.count_items() < 1
    bm25_conn.create(init_instance)
    assert bm25_conn.count_items() == len(init_instance)

    try:
        bm25_conn.upsert(list(new_instances.values()))
    except ValueError as e:
        print(str(e))
        assert exception
    else:
        assert not exception

        real_contents = bm25_conn.read(list(new_instances.keys()))
        assert len(real_contents) == len(new_instances)
        for item in real_contents:
            assert item.document == new_instances[item.id].document
            assert item.embedding is None
            assert item.metadata == new_instances[item.id].metadata

        real_count = bm25_conn.count_items()
        assert real_count == expected_count


@pytest.mark.parametrize("instances, delete_ids, expected, bm25_conn",
                         BM25_POPULATED_DELETE_TEST_CASES, indirect=['bm25_conn'])
def test_delete(instances, delete_ids, expected, bm25_conn: AbstractVectorDatabaseConnection):
    bm25_conn.clear()
    bm25_conn.create(instances)

    try:
        bm25_conn.delete(delete_ids)
    except ValueError as e:
        print(str(e))
        assert expected['exception']
    else:
        assert not expected['exception']
        for d_id in delete_ids:
            assert not bm25_conn.item_exist(d_id)

        assert bm25_conn.count_items() == expected['db_size']


@pytest.mark.parametrize("instances, queries, n_results, subset_ids, expected, bm25_conn",
                         BM25_POPULATED_RETRIEVE_TEST_CASES, indirect=['bm25_conn'])
def test_retrieve(instances: List[VectorDBInstance], queries: List[str], n_results: int, subset_ids: List[str],
                  expected: Dict[str, object], bm25_conn: AbstractVectorDatabaseConnection):
    bm25_conn.clear()
    bm25_conn.create(instances)
    for item in instances:
        assert bm25_conn.item_exist(item.id)
    assert bm25_conn.count_items() == len(instances)

    try:
        output = bm25_conn.retrieve(
            queries, n_results=n_results, subset_ids=subset_ids)
    except (ValueError, AssertionError, ParamError, MilvusException) as e:
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


@pytest.mark.parametrize("instances, expected, bm25_conn",
                         BM25_POPULATED_COUNT_TEST_CASES,
                         indirect=['bm25_conn'])
def test_count_items(instances: List[VectorDBInstance], expected: Dict[str, int],
                     bm25_conn: AbstractVectorDatabaseConnection):
    bm25_conn.clear()
    assert bm25_conn.count_items() == 0

    bm25_conn.create(instances)
    assert bm25_conn.count_items() == expected


@pytest.mark.parametrize("instances, input_id, expected, bm25_conn",
                         BM25_POPULATED_EXIST_TEST_CASES, indirect=['bm25_conn'])
def test_item_exist(instances: List[VectorDBInstance], input_id: object, expected: Dict[str, object],
                    bm25_conn: AbstractVectorDatabaseConnection):
    bm25_conn.clear()
    bm25_conn.create(instances)

    try:
        real = bm25_conn.item_exist(input_id)
    except ValueError as e:
        print(str(e))
        assert expected['exception']
    else:
        assert not expected['exception']
        assert real == expected['exist']


@pytest.mark.parametrize("instances, bm25_conn", BM25_POPULATED_CLEAR_TEST_CASES, indirect=['bm25_conn'])
def test_clear(instances: List[VectorDBInstance], bm25_conn: AbstractVectorDatabaseConnection):
    bm25_conn.clear()
    assert bm25_conn.count_items() == 0

    bm25_conn.create(instances)
    assert bm25_conn.count_items() == len(instances)

    bm25_conn.clear()
    assert bm25_conn.count_items() == 0
