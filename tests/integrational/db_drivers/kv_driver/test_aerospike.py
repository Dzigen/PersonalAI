import pytest
from chromadb.errors import ChromaError

import sys
sys.path.insert(0, "../../")

from cases import KVDB_CREAT_TEST_CASES, KVDB_DELETE_TEST_CASES, \
    KVDB_READ_TEST_CASES, KVDB_COUNT_TEST_CASES, KVDB_EXIST_TEST_CASES, \
    KVDB_CLEAR_TEST_CASES

@pytest.mark.parametrize("input, expected", KVDB_CREAT_TEST_CASES)
def test_create(input, expected, aerospike_conn):
    aerospike_conn.clear()

    try:
        for inp in input:
            aerospike_conn.create(inp)
    except Exception as e:
        print(str(e))
        assert expected['exception']

    assert aerospike_conn.count_items() == expected['db_size']

@pytest.mark.parametrize("instances, input, expected", KVDB_DELETE_TEST_CASES)
def test_delete(instances, input, expected, aerospike_conn):
    aerospike_conn.clear()
    aerospike_conn.create(instances)

    try:
        aerospike_conn.delete(input)
    except Exception as e:
        print(str(e))
        assert expected['exception']

    assert aerospike_conn.count_items() == expected['db_size']


@pytest.mark.parametrize("instances, input, expected", KVDB_READ_TEST_CASES)
def test_read(instances, input, expected, aerospike_conn):
    aerospike_conn.clear()
    aerospike_conn.create(instances)

    try:
        output = aerospike_conn.read(input)
    except Exception as e:
        print(str(e))
        assert expected['exception']

    if not expected['exception']:
        assert list(map(lambda item: item.id, output)) == expected['output_ids']


@pytest.mark.parametrize("instances, expected", KVDB_COUNT_TEST_CASES)
def test_count(instances, expected, aerospike_conn):
    aerospike_conn.clear()
    aerospike_conn.create(instances)

    assert aerospike_conn.count_items() == expected


@pytest.mark.parametrize("instances, input, expected", KVDB_EXIST_TEST_CASES)
def test_exist(instances, input, expected, aerospike_conn):
    aerospike_conn.clear()
    aerospike_conn.create(instances)

    try:
        real = aerospike_conn.item_exist(input)
    except Exception as e:
        print(str(e))
        assert expected['exception']

    if not expected['exception']:
        assert real == expected['exist']


@pytest.mark.parametrize("instances", KVDB_CLEAR_TEST_CASES)
def test_clear(instances, aerospike_conn):
    aerospike_conn.clear()
    aerospike_conn.create(instances)

    assert aerospike_conn.count_items() == len(instances)
    aerospike_conn.clear()
    assert aerospike_conn.count_items() == 0
