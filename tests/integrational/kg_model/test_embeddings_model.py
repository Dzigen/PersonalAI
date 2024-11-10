import pytest

import sys
sys.path.insert(0, "../../")
import pytest

from cases import EM_CREATE_TESTS, EM_DELETE_TESTS

@pytest.mark.parametrize("triplets, add_nodes_flag, expected", EM_CREATE_TESTS)
def test_create_triplets(triplets, add_nodes_flag, expected, embeddings_model):
    embeddings_model.vectordbs['nodes'].clear()
    embeddings_model.vectordbs['triplets'].clear()

    created_item_ids = embeddings_model.create_triplets(triplets, add_nodes=add_nodes_flag, batch_size=128)

    real_nodes_db_size = embeddings_model.vectordbs['nodes'].count_items()
    real_triplets_db_size = embeddings_model.vectordbs['triplets'].count_items()
    assert real_nodes_db_size == expected['nodes_count']
    assert real_triplets_db_size == expected['triplets_count']
    assert real_nodes_db_size == len(created_item_ids['nodes'])
    assert real_triplets_db_size == len(created_item_ids['triplets'])

    if add_nodes_flag:
        for node_id in created_item_ids['nodes']:
            assert embeddings_model.vectordbs['nodes'].item_exist(node_id)
    for triplet_id in created_item_ids['triplets']:
        assert embeddings_model.vectordbs['triplets'].item_exist(triplet_id)

@pytest.mark.parametrize("base_triplets, triplets_to_delete, delete_nodes_flag, expected", EM_DELETE_TESTS)
def test_delete_triplets(triplets. expected, embeddings_model):
    embeddings_model.vectordbs['nodes'].clear()
    embeddings_model.vectordbs['triplets'].clear()

    embeddings_model.create_triplets(base_triplets, create_nodes=True)
    deleted_item_ids = embeddings_model.delete_triplets(triplets_to_delete, delete_nodes=delete_nodes_flag)

    real_nodes_db_size = embeddings_model.vectordbs['nodes'].count_items()
    real_triplets_db_size = embeddings_model.vectordbs['triplets'].count_items()
    assert real_nodes_db_size == expected['nodes_count']
    assert real_triplets_db_size == expected['triplets_count']

    assert len(deleted_item_ids['nodes']) == expected['deleted_n_count']
    assert len(deleted_item_ids['triplets']) == len(deleted_item_ids['deleted_t_count'])

    if add_nodes_flag:
        for node_id in deleted_item_ids['nodes']:
            assert not embeddings_model.vectordbs['nodes'].item_exist(node_id)
    for triplet_id in deleted_item_ids['triplets']:
        assert not embeddings_model.vectordbs['triplets'].item_exist(triplet_id)
