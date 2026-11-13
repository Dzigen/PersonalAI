import pytest
from chromadb.errors import ChromaError
import sys
sys.path.insert(0, "../")

from typing import List
from src.db_drivers.kv_driver.utils import AbstractKVDatabaseConnection

from .cases import KVDB_POPULATED_CREATE_TEST_CASES, KVDB_POPULATED_DELETE_TEST_CASES, \
    KVDB_POPULATED_READ_TEST_CASES, KVDB_POPULATED_COUNT_TEST_CASES, KVDB_POPULATED_EXIST_TEST_CASES, \
    KVDB_POPULATED_CLEAR_TEST_CASES, KVDB_POPULATED_IS_OPEN_TEST_CASES


@pytest.mark.parametrize("input, expected, kvdb_conn",
                         KVDB_POPULATED_CREATE_TEST_CASES,
                         indirect=['kvdb_conn'])
def test_create(input, expected, kvdb_conn):
    kvdb_conn.clear()

    try:
        for inp in input:
            kvdb_conn.create(inp)
    except ValueError as e:
        print(str(e))
        assert expected['exception']
    else:
        assert not expected['exception']

    assert kvdb_conn.count_items() == expected['db_size']


@pytest.mark.parametrize("instances, input, expected, kvdb_conn",
                         KVDB_POPULATED_DELETE_TEST_CASES, indirect=['kvdb_conn'])
def test_delete(instances, input, expected, kvdb_conn):
    kvdb_conn.clear()
    kvdb_conn.create(instances)

    try:
        kvdb_conn.delete(input)
    except ValueError as e:
        print(str(e))
        assert expected['exception']
    else:
        assert not expected['exception']

    assert kvdb_conn.count_items() == expected['db_size']


@pytest.mark.parametrize("instances, input, expected, kvdb_conn",
                         KVDB_POPULATED_READ_TEST_CASES, indirect=['kvdb_conn'])
def test_read(instances, input, expected, kvdb_conn):
    kvdb_conn.clear()
    kvdb_conn.create(instances)

    try:
        output = kvdb_conn.read(input)
    except ValueError as e:
        print(str(e))
        assert expected['exception']
    else:
        assert not expected['exception']

    if not expected['exception']:
        assert list(map(lambda item: None if item is None else item.id,
                    output)) == expected['output_ids']


@pytest.mark.parametrize("instances, expected, kvdb_conn",
                         KVDB_POPULATED_COUNT_TEST_CASES, indirect=['kvdb_conn'])
def test_count(instances, expected, kvdb_conn):
    kvdb_conn.clear()
    kvdb_conn.create(instances)

    assert kvdb_conn.count_items() == expected


@pytest.mark.parametrize("instances, input, expected, kvdb_conn",
                         KVDB_POPULATED_EXIST_TEST_CASES, indirect=['kvdb_conn'])
def test_exist(instances, input, expected, kvdb_conn):
    kvdb_conn.clear()
    kvdb_conn.create(instances)

    try:
        real = kvdb_conn.item_exist(input)
    except ValueError as e:
        print(str(e))
        assert expected['exception']
    else:
        assert not expected['exception']

    if not expected['exception']:
        assert real == expected['exist']


@pytest.mark.parametrize("instances, kvdb_conn", KVDB_POPULATED_CLEAR_TEST_CASES, indirect=['kvdb_conn'])
def test_clear(instances, kvdb_conn):
    kvdb_conn.clear()
    kvdb_conn.create(instances)

    assert kvdb_conn.count_items() == len(instances)
    kvdb_conn.clear()
    assert kvdb_conn.count_items() == 0


@pytest.mark.parametrize("conn_sequence, kvdb_conn", KVDB_POPULATED_IS_OPEN_TEST_CASES, indirect=['kvdb_conn'])
def test_is_open(conn_sequence: List[str], kvdb_conn: AbstractKVDatabaseConnection):
    assert kvdb_conn.is_open()

    for conn_kw in conn_sequence:
        if conn_kw == 'open':
            kvdb_conn.open_connection()
            assert kvdb_conn.is_open()
        elif conn_kw == 'close':
            kvdb_conn.close_connection()
            assert not kvdb_conn.is_open()
        else:
            raise ValueError

    kvdb_conn.open_connection()
    assert kvdb_conn.is_open()
