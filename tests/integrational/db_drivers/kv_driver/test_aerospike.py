import pytest
from chromadb.errors import ChromaError

import sys
sys.path.insert(0, "../../")

from cases import KVDB_CREAT_TEST_CASES, KVDB_DELETE_TEST_CASES, \
    KVDB_READ_TEST_CASES, KVDB_COUNT_TEST_CASES, KVDB_EXIST_TEST_CASES, \
    KVDB_CLEAR_TEST_CASES

@pytest.mark.parametrize("input, expected", KVDB_CREAT_TEST_CASES)
def test_create(input, expected, aerospike_conn):
    pass


@pytest.mark.parametrize("input, expected", KVDB_DELETE_TEST_CASES)
def test_delete(input, expected, aerospike_conn):
    pass


@pytest.mark.parametrize("input, expected", KVDB_READ_TEST_CASES)
def test_read(input, expected, aerospike_conn):
    pass


@pytest.mark.parametrize("input, expected", KVDB_COUNT_TEST_CASES)
def test_count(input, expected, aerospike_conn):
    pass


@pytest.mark.parametrize("input, expected", KVDB_EXIST_TEST_CASES)
def test_exist(input, expected, aerospike_conn):
    pass


@pytest.mark.parametrize("input, expected", KVDB_CLEAR_TEST_CASES)
def test_clear(input, expected, aerospike_conn):
    pass
