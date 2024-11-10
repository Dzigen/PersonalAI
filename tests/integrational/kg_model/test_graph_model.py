import pytest

from cases import GM_CREATE_TESTS, GM_DELETE_TESTS

@pytest.mark.parametrize("triplets, expected", GM_CREATE_TESTS)
def test_create_triplets(triplets, expected, graph_model):
    graph_model.db_conn.clear()
    created_item_ids = graph_model.create_triplets(triplets, batch_size=1)
    assert created_item_ids['nodes'] == expected['nodes_count']
    assert created_item_ids['triplets'] == expected['triplets_count']

    for node_id in created_item_ids['nodes']:
        assert item_exist(node_id, id_type='node')
    for triplet_id in created_item_ids['triplets']:
        assert item_exist(triplet_id, id_type='triplet')


@pytest.mark.parametrize("base_triplets, triplets_to_delete, expected", GM_DELETE_TESTS)
def test_delete_triplets(base_triplets, triplets_to_delete, expected, graph_model):
    graph_model.db_conn.clear()
    created_item_ids = graph_model.create_triplets(triplets, batch_size=1)
    assert created_item_ids['nodes'] == expected['nodes_count']
    assert created_item_ids['triplets'] == expected['triplets_count']

    deleted_item_ids = graph_model.delete_triplets(triplets_to_delete,batch_size=1)

    assert len(deleted_item_ids['nodes']) == len(expected['deleted_n_count'])
    assert len(deleted_item_ids['triplets']) == len(deleted_item_ids['deleted_t_count'])

    for node_id in deleted_item_ids['nodes']:
        assert not item_exist(node_id, id_type='node')
    for triplet_id in deleted_item_ids['triplets']:
        assert not item_exist(triplet_id, id_type='triplet')
