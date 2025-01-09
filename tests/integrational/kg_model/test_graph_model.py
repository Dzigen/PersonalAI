import pytest

import sys
sys.path.insert(0, "../")
import pytest

from cases import GM_POPULATED_CREATE_TEST_CASES, GM_POPULATED_DELETE_TEST_CASES

@pytest.mark.parametrize("triplets, expected, graph_model", GM_POPULATED_CREATE_TEST_CASES, indirect=['graph_model'])
def test_create_triplets(triplets, expected, graph_model):
    graph_model.db_conn.clear()
    created_item_ids = graph_model.create_triplets(triplets, batch_size=1)
    assert len(created_item_ids['nodes']) == expected['nodes_count']
    assert len(created_item_ids['triplets']) == expected['triplets_count']

    for node_id in created_item_ids['nodes']:
        assert graph_model.db_conn.item_exist(node_id, id_type='node')
    for triplet_id in created_item_ids['triplets']:
        assert graph_model.db_conn.item_exist(triplet_id, id_type='triplet')

@pytest.mark.parametrize("init_triplets, triplets_to_delete, expected_delete_n_info, expected_init_count, expected_final_count, graph_model", GM_POPULATED_DELETE_TEST_CASES, indirect=['graph_model'])
def test_delete_triplets(init_triplets, triplets_to_delete, expected_delete_n_info, expected_initexpected_init_count, expected_final_count, graph_model):
    graph_model.db_conn.clear()
    created_item_ids = graph_model.create_triplets(init_triplets, batch_size=1)
    assert created_item_ids['nodes'] == expected_init_count['nodes_count']
    assert created_item_ids['triplets'] == expected_init_count['triplets_count']

    nodes_delete_info = graph_model.delete_triplets(triplets_to_delete, batch_size=1)

    for real_delete_info, expected_delete_info in zip(nodes_delete_info, expected_delete_n_info):
        assert real_delete_info == expected_delete_info

    for node_id in deleted_item_ids['nodes']:
        assert not graph_model.db_conn.item_exist(node_id, id_type='node')
    for triplet_id in deleted_item_ids['triplets']:
        assert not graph_model.db_conn.item_exist(triplet_id, id_type='triplet')
