import pytest
from chromadb.errors import ChromaError

import sys
sys.path.insert(0, "../../")

from cases import GRAPHDB_CREATE_TEST_CASES, GRAPHDB_DELETE_TEST_CASES, \
    GRAPHDB_READ_TEST_CASES, GRAPHDB_COUNT_TEST_CASES, GRAPHDB_EXIST_TEST_CASES, \
    GRAPHDB_CLEAR_TEST_CASES, GRAPHDB_GET_TRIPLETS_TEST_CASES, GRAPHDB_GET_ADJECENT_TEST_CASES

@pytest.mark.parametrize("inputs, create_info, expected", GRAPHDB_CREATE_TEST_CASES)
def test_create(inputs, create_info, expected, inmemory_conn):
    inmemory_conn.clear()

    try:
        for inp, info in zip(inputs, create_info):
            inmemory_conn.create(inp, info)
    except Exception as e:
        print(str(e))
        assert expected['exception']
    else:
        assert not expected['exception']

    items_info = inmemory_conn.count_items()
    assert items_info['triplets'] == expected['triplets_count']
    assert items_info['nodes'] == expected['nodes_count']

@pytest.mark.parametrize("instances, create_info, inputs, expected", GRAPHDB_DELETE_TEST_CASES)
def test_delete(instances, create_info, inputs, expected, inmemory_conn):
    inmemory_conn.clear()
    inmemory_conn.create(instances, create_info)

    try:
        inmemory_conn.delete(inputs)
    except Exception as e:
        print(str(e))
        assert expected['exception']
    else:
        assert not expected['exception']

    items_info = inmemory_conn.count_items()
    assert items_info['triplets'] == expected['triplets_count']
    assert items_info['nodes'] == expected['nodes_count']


@pytest.mark.parametrize("instances, create_info, inputs, expected", GRAPHDB_READ_TEST_CASES)
def test_read(instances, create_info, inputs, expected, inmemory_conn):
    inmemory_conn.clear()
    inmemory_conn.create(instances, create_info)

    try:
        output = inmemory_conn.read(inputs)
    except Exception as e:
        print(str(e))
        assert expected['exception']
    else:
        assert not expected['exception']

    if not expected['exception']:
        assert list(map(lambda item: item.id, output)) == expected['output_ids']


@pytest.mark.parametrize("instances, create_info, expected", GRAPHDB_COUNT_TEST_CASES)
def test_count(instances, create_info, expected, inmemory_conn):
    inmemory_conn.clear()
    inmemory_conn.create(instances, create_info)

    items_info = inmemory_conn.count_items()
    assert items_info['triplets'] == expected['triplets_count']
    assert items_info['nodes'] == expected['nodes_count']


@pytest.mark.parametrize("instances, inputs, expected", GRAPHDB_EXIST_TEST_CASES)
def test_exist(instances, inputs, expected, inmemory_conn):
    inmemory_conn.clear()
    inmemory_conn.create(instances)

    try:
        real = inmemory_conn.item_exist(inputs)
    except Exception as e:
        print(str(e))
        assert expected['exception']
    else:
        assert not expected['exception']

    if not expected['exception']:
        assert real == expected['exist']


@pytest.mark.parametrize("instances, expected", GRAPHDB_CLEAR_TEST_CASES)
def test_clear(instances, expected, inmemory_conn):
    inmemory_conn.clear()
    inmemory_conn.create(instances)

    items_info = inmemory_conn.count_items()
    assert items_info['triplets'] == len(instances)
    assert items_info['nodes'] == 2*len(instances)

    inmemory_conn.clear()

    items_info = inmemory_conn.count_items()
    assert items_info['triplets'] == 0
    assert items_info['nodes'] == 0

@pytest.mark.parametrize("instances, create_info, node, accepted_n_types, expected", GRAPHDB_GET_ADJECENT_TEST_CASES)
def test_get_adjecent_nodes(instances, create_info, node, accepted_n_types, expected, inmemory_conn):
    inmemory_conn.clear()
    inmemory_conn.create(instances, create_info)

    try:
        output = inmemory_conn.get_adjecent_nodes(node, accepted_n_types=accepted_n_types)
    except Exception as e:
        print(str(e))
        assert expected['exception']
    else:
        assert not expected['exception']

    assert expected['output_ids'] == set(output)


@pytest.mark.parametrize("instances, create_info, nodes, expected", GRAPHDB_GET_TRIPLETS_TEST_CASES)
def test_get_triplets(instances, create_info, nodes, expected, inmemory_conn):
    inmemory_conn.clear()
    inmemory_conn.create(instances, create_info)

    try:
        output = inmemory_conn.get_triplets(*nodes)
    except Exception as e:
        print(str(e))
        assert expected['exception']
    else:
        assert not expected['exception']

    assert expected['output_ids'] == set(list(map(lambda triplet: triplet.id, output)))
