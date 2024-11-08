import pytest
from chromadb.errors import ChromaError

import sys
sys.path.insert(0, "../../")

from cases import GRAPHDB_CREAT_TEST_CASES, GRAPHDB_DELETE_TEST_CASES, \
    GRAPHDB_READ_TEST_CASES, GRAPHDB_COUNT_TEST_CASES, GRAPHDB_EXIST_TEST_CASES, \
    GRAPHDB_CLEAR_TEST_CASES

@pytest.mark.parametrize("input, expected", GRAPHDB_CREAT_TEST_CASES)
def test_create(input, expected, neo4j_conn):
    pass


@pytest.mark.parametrize("input, expected", GRAPHDB_DELETE_TEST_CASES)
def test_delete(input, expected, neo4j_conn):
    pass


@pytest.mark.parametrize("input, expected", GRAPHDB_READ_TEST_CASES)
def test_read(input, expected, neo4j_conn):
    pass


@pytest.mark.parametrize("input, expected", GRAPHDB_COUNT_TEST_CASES)
def test_count(input, expected, neo4j_conn):
    pass


@pytest.mark.parametrize("input, expected", GRAPHDB_EXIST_TEST_CASES)
def test_exist(input, expected, neo4j_conn):
    pass


@pytest.mark.parametrize("input, expected", GRAPHDB_CLEAR_TEST_CASES)
def test_clear(input, expected, neo4j_conn):
    pass
