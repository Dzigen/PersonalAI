import pytest
from typing import List, Tuple, Dict, Union

import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from cases import TESTDB_POPULATED_CREATE_TEST_CASES, TESTDB_POPULATED_READ_TEST_CASES, \
    TESTDB_POPULATED_UPDATE_TEST_CASES, TESTDB_POPULATED_DELETE_TEST_CASES, \
        TESTDB_POPULATED_COUNT_TEST_CASES, TESTDB_POPULATED_EXIST_TEST_CASES, \
            TESTDB_POPULATED_CLEAR_TEST_CASES, TESTDB_POPULATED_GETCHILDS_TEST_CASES

from src.utils import Triplet, RelationType, NodeType
from src.utils.data_structs import Node
from src.db_drivers.tree_driver.utils import AbstractTreeDatabaseConnection

@pytest.mark.parametrize("parent_id, child_data, expected, treedb_conn", TESTDB_POPULATED_CREATE_TEST_CASES, indirect=['treedb_conn'])
def test_create(parent_id, child_data, expected, treedb_conn):
    # TODO
    pass

@pytest.mark.parametrize("create_pairs, read_ids, type, expected, treedb_conn", TESTDB_POPULATED_READ_TEST_CASES, indirect=['treedb_conn'])
def test_read(create_pairs, read_ids, type, expected, treedb_conn):
    # TODO
    pass

@pytest.mark.parametrize("create_pairs, update_nodes, treedb_conn", TESTDB_POPULATED_UPDATE_TEST_CASES, indirect=['treedb_conn'])
def test_update(create_pairs, update_nodes, treedb_conn):
    # TODO
    pass

@pytest.mark.parametrize("create_pairs, delete_ids, type, treedb_conn", TESTDB_POPULATED_DELETE_TEST_CASES, indirect=['treedb_conn'])
def test_delete(create_pairs, delete_ids, type, treedb_conn):
    # TODO
    pass

@pytest.mark.parametrize("create_pairs, expected_count, treedb_conn", TESTDB_POPULATED_COUNT_TEST_CASES, indirect=['treedb_conn'])
def test_countitems(create_pairs, expected_count, treedb_conn):
    # TODO
    pass

@pytest.mark.parametrize("create_pairs, node_id, type, treedb_conn", TESTDB_POPULATED_EXIST_TEST_CASES, indirect=['treedb_conn'])
def test_itemexist(create_pairs, node_id, type, treedb_conn):
    # TODO
    pass

@pytest.mark.parametrize("create_pairs, treedb_conn", TESTDB_POPULATED_CLEAR_TEST_CASES, indirect=['treedb_conn'])
def test_clear(create_pairs, treedb_conn):
    # TODO
    pass

@pytest.mark.parametrize("create_pairs, parent_id, expected_child_nodes, treedb_conn", TESTDB_POPULATED_GETCHILDS_TEST_CASES, indirect=['treedb_conn'])
def test_getchildnodes(create_pairs, parent_id, expected_child_nodes, treedb_conn):
    # TODO
    pass
