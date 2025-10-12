import pytest
from typing import List, Dict
import sys
from copy import deepcopy
sys.path.insert(0, "../")

from src.db_drivers.table_driver import TableDBInstance
from src.db_drivers.utils import AbstractDatabaseConnection

from .cases import TABLEDB_POPULATED_CREATE_TEST_CASES, TABLEDB_POPULATED_DELETE_TEST_CASES, \
    TABLEDB_POPULATED_READ_TEST_CASES, TABLEDB_POPULATED_COUNT_TEST_CASES, TABLEDB_POPULATED_EXIST_TEST_CASES, \
    TABLEDB_POPULATED_CLEAR_TEST_CASES


@pytest.mark.parametrize("input, expected, tabledb_conn",
                         TABLEDB_POPULATED_CREATE_TEST_CASES,
                         indirect=['tabledb_conn'])
def test_create(input: List[TableDBInstance], expected: Dict, tabledb_conn: AbstractDatabaseConnection):
    tabledb_conn.clear()

    input = deepcopy(input)

    try:
        for inp in input:
            tabledb_conn.create(inp)
    except (TypeError, ValueError) as e:
        print(str(e))
        assert expected['exception']
    else:
        assert not expected['exception']

    assert tabledb_conn.count_items() == expected['db_size']


@pytest.mark.parametrize("instances, input, expected, tabledb_conn",
                         TABLEDB_POPULATED_DELETE_TEST_CASES, indirect=['tabledb_conn'])
def test_delete(instances: List[TableDBInstance], input: List[str], expected: Dict, tabledb_conn: AbstractDatabaseConnection):
    tabledb_conn.clear()
    instances = deepcopy(instances)

    tabledb_conn.create(instances)

    try:
        tabledb_conn.delete(input)
    except (TypeError,ValueError) as e:
        print(str(e))
        assert expected['exception']
    else:
        assert not expected['exception']

    assert tabledb_conn.count_items() == expected['db_size']


@pytest.mark.parametrize("instances, input, expected, tabledb_conn",
                         TABLEDB_POPULATED_READ_TEST_CASES, indirect=['tabledb_conn'])
def test_read(instances: List[TableDBInstance], input: List[str], expected: Dict, tabledb_conn: AbstractDatabaseConnection):
    tabledb_conn.clear()
    instances = deepcopy(instances)
    tabledb_conn.create(instances)

    try:
        output = tabledb_conn.read(input)
    except (TypeError,ValueError) as e:
        print(str(e))
        assert expected['exception']
    else:
        assert not expected['exception']

    if not expected['exception']:
        assert list(map(lambda item: None if item is None else item.id,
                    output)) == expected['output_ids']


@pytest.mark.parametrize("instances, expected, tabledb_conn",
                         TABLEDB_POPULATED_COUNT_TEST_CASES, indirect=['tabledb_conn'])
def test_count(instances: List[TableDBInstance], expected: int, tabledb_conn: AbstractDatabaseConnection):
    tabledb_conn.clear()
    assert tabledb_conn.count_items() == 0

    instances = deepcopy(instances)
    tabledb_conn.create(instances)
    assert tabledb_conn.count_items() == expected


@pytest.mark.parametrize("instances, input, expected, tabledb_conn",
                         TABLEDB_POPULATED_EXIST_TEST_CASES, indirect=['tabledb_conn'])
def test_exist(instances: List[TableDBInstance], input: str, expected: Dict, tabledb_conn: AbstractDatabaseConnection):
    tabledb_conn.clear()
    instances = deepcopy(instances)
    tabledb_conn.create(instances)

    try:
        real = tabledb_conn.item_exist(input)
    except (TypeError,ValueError) as e:
        print(str(e))
        assert expected['exception']
    else:
        assert not expected['exception']

    if not expected['exception']:
        assert real == expected['exist']


@pytest.mark.parametrize("instances, tabledb_conn", TABLEDB_POPULATED_CLEAR_TEST_CASES, indirect=['tabledb_conn'])
def test_clear(instances: List[TableDBInstance], tabledb_conn: AbstractDatabaseConnection):
    tabledb_conn.clear()
    assert tabledb_conn.count_items() == 0

    instances = deepcopy(instances)
    tabledb_conn.create(instances)
    assert tabledb_conn.count_items() == len(instances)

    tabledb_conn.clear()
    assert tabledb_conn.count_items() == 0
