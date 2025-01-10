import pytest

import sys
sys.path.insert(0, "../")
import pytest

from cases import GM_POPULATED_CREATE_TEST_CASES, GM_POPULATED_DELETE_TEST_CASES

@pytest.mark.parametrize("init_triplets, expected_init_count, expected_create_info, graph_model", GM_POPULATED_CREATE_TEST_CASES, indirect=['graph_model'])
def test_create_triplets(init_triplets, expected_init_count, expected_create_info, graph_model):
    graph_model.db_conn.clear()

    real_create_info = graph_model.create_triplets(init_triplets, batch_size=1)
    assert real_create_info['nodes'] == expected_create_info['nodes']
    assert real_create_info['triplets'] == expected_create_info['triplets']

    real_items_count = graph_model.count_items()
    assert real_items_count['nodes'] == expected_init_count['nodes']
    assert real_items_count['triplets'] == expected_init_count['triplets']

    for node_id in real_create_info['nodes']:
        assert graph_model.db_conn.item_exist(node_id, id_type='node')
    for triplet_id in real_create_info['triplets']:
        assert graph_model.db_conn.item_exist(triplet_id, id_type='triplet')

    for triplet in init_triplets:
        assert graph_model.db_conn.item_exist(triplet.start_node.id, id_type='node')
        assert graph_model.db_conn.item_exist(triplet.end_node.id, id_type='node')
        assert graph_model.db_conn.item_exist(triplet.id, id_type='triplet')
        assert graph_model.db_conn.item_exist(triplet.realtion.id, id_type='realation')

@pytest.mark.parametrize("init_triplets, expected_create_info, expected_init_count, triplets_to_delete, expected_delete_n_info, expected_final_count, graph_model", GM_POPULATED_DELETE_TEST_CASES, indirect=['graph_model'])
def test_delete_triplets(init_triplets, expected_create_info, expected_init_count, triplets_to_delete, expected_delete_n_info, expected_final_count, graph_model):
    graph_model.db_conn.clear()

    real_create_info = graph_model.create_triplets(init_triplets, batch_size=1)
    assert real_create_info['nodes'] == expected_create_info['nodes']
    assert real_create_info['triplets'] == expected_create_info['triplets']

    real_items_count = graph_model.count_items()
    assert real_items_count['nodes'] == expected_init_count['nodes']
    assert real_items_count['triplets'] == expected_init_count['triplets']

    nodes_delete_info = graph_model.delete_triplets(triplets_to_delete, batch_size=1)

    for real_delete_info, expected_delete_info in zip(nodes_delete_info, expected_delete_n_info):
        assert real_delete_info == expected_delete_info

    real_items_count = graph_model.count_items()
    assert real_items_count['nodes'] == expected_final_count['nodes']
    assert real_items_count['triplets'] == expected_final_count['triplets']

    for triplet, delete_info in zip(triplets_to_delete, nodes_delete_info):
        assert not graph_model.db_conn.item_exist(triplet.id, id_type='triplet')
        if delete_info['s_node']:
            assert not graph_model.db_conn.item_exist(triplet.start_node.id, id_type='node')
        if delete_info['e_node']:
            assert not graph_model.db_conn.item_exist(triplet.end_node.id, id_type='node')
