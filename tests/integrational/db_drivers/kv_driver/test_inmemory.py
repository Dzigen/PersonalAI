import pytest
from chromadb.errors import ChromaError

import sys
sys.path.insert(0, "../../")

from cases import KVDB_CREAT_TEST_CASES, KVDB_DELETE_TEST_CASES, \
    KVDB_READ_TEST_CASES, KVDB_COUNT_TEST_CASES, KVDB_EXIST_TEST_CASES, \
    KVDB_CLEAR_TEST_CASES

@pytest.mark.parametrize("input, expected", KVDB_CREAT_TEST_CASES)
def test_create(input, expected, inmemory_conn):
    inmemory_conn.clear()

    try:
        for inp in input:
            inmemory_conn.create(inp)
    except Exception as e:
        print(str(e))
        assert expected['exception']

    assert inmemory_conn.count_items() == expected['db_size']

@pytest.mark.parametrize("instances, input, expected", KVDB_DELETE_TEST_CASES)
def test_delete(instances, input, expected, inmemory_conn):
    inmemory_conn.clear()
    inmemory_conn.create(instances)

    try:
        inmemory_conn.delete(input)
    except ValueError as e:
        print(str(e))
        assert expected['exception']

    assert inmemory_conn.count_items() == expected['db_size']


@pytest.mark.parametrize("instances, input, expected", KVDB_READ_TEST_CASES)
def test_read(instances, input, expected, inmemory_conn):
    inmemory_conn.clear()
    inmemory_conn.create(instances)

    try:
        output = inmemory_conn.read(input)
    except Exception as e:
        print(str(e))
        assert expected['exception']

    if not expected['exception']:
        assert list(map(lambda item: item.id, output)) == expected['output_ids']


@pytest.mark.parametrize("instances, expected", KVDB_COUNT_TEST_CASES)
def test_count(instances, expected, inmemory_conn):
    inmemory_conn.clear()
    inmemory_conn.create(instances)

    assert inmemory_conn.count_items() == expected


@pytest.mark.parametrize("instances, input, expected", KVDB_EXIST_TEST_CASES)
def test_exist(instances, input, expected, inmemory_conn):
    inmemory_conn.clear()
    inmemory_conn.create(instances)

    try:
        real = inmemory_conn.item_exist(input)
    except Exception as e:
        print(str(e))
        assert expected['exception']

    if not expected['exception']:
        assert real == expected['exist']


@pytest.mark.parametrize("instances", KVDB_CLEAR_TEST_CASES)
def test_clear(instances, inmemory_conn):
    inmemory_conn.clear()
    inmemory_conn.create(instances)

    assert inmemory_conn.count_items() == len(instances)
    inmemory_conn.clear()
    assert inmemory_conn.count_items() == 0
