import pytest
from chromadb.errors import ChromaError

import sys
sys.path.insert(0, "../../")

from cases import GRAPHDB_CREAT_TEST_CASES, GRAPHDB_DELETE_TEST_CASES, \
    GRAPHDB_READ_TEST_CASES, GRAPHDB_COUNT_TEST_CASES, GRAPHDB_EXIST_TEST_CASES, \
    GRAPHDB_CLEAR_TEST_CASES

@pytest.mark.parametrize("input, expected", GRAPHDB_CREAT_TEST_CASES)
def test_create(input, expected, neo4j_conn):
    neo4j_conn.clear()

    try:
        for inp in input:
            neo4j_conn.create(inp)
    except Exception as e:
        print(str(e))
        assert expected['exception']

    assert neo4j_conn.count_items() == expected['db_size']

@pytest.mark.parametrize("instances, input, expected", GRAPHDB_DELETE_TEST_CASES)
def test_delete(instances, input, expected, neo4j_conn):
    neo4j_conn.clear()
    neo4j_conn.create(instances)

    try:
        neo4j_conn.delete(input)
    except Exception as e:
        print(str(e))
        assert expected['exception']

    assert neo4j_conn.count_items() == expected['db_size']


@pytest.mark.parametrize("instances, input, expected", GRAPHDB_READ_TEST_CASES)
def test_read(instances, input, expected, neo4j_conn):
    neo4j_conn.clear()
    neo4j_conn.create(instances)

    try:
        output = neo4j_conn.read(input)
    except Exception as e:
        print(str(e))
        assert expected['exception']

    if not expected['exception']:
        assert list(map(lambda item: item.id, output)) == expected['output_ids']


@pytest.mark.parametrize("instances, expected", GRAPHDB_COUNT_TEST_CASES)
def test_count(instances, expected, neo4j_conn):
    neo4j_conn.clear()
    neo4j_conn.create(instances)

    assert neo4j_conn.count_items() == expected


@pytest.mark.parametrize("instances, input, expected", GRAPHDB_EXIST_TEST_CASES)
def test_exist(instances, input, expected, neo4j_conn):
    neo4j_conn.clear()
    neo4j_conn.create(instances)

    try:
        real = neo4j_conn.item_exist(input)
    except Exception as e:
        print(str(e))
        assert expected['exception']

    if not expected['exception']:
        assert real == expected['exist']


@pytest.mark.parametrize("instances", GRAPHDB_CLEAR_TEST_CASES)
def test_clear(instances, neo4j_conn):
    neo4j_conn.clear()
    neo4j_conn.create(instances)

    assert neo4j_conn.count_items() == len(instances)
    neo4j_conn.clear()
    assert neo4j_conn.count_items() == 0
