import pytest

import sys
sys.path.insert(0, "../")
import pytest

from cases import EM_POPULATED_CREATE_TEST_CASES, EM_POPULATED_DELETE_TEST_CASES

@pytest.mark.parametrize("init_triplets, add_nodes_flag, expected_init_count, expected_creation_info, embeddings_model", EM_POPULATED_CREATE_TEST_CASES, indirect=['embeddings_model'])
def test_create_triplets(init_triplets, add_nodes_flag, expected_init_count, expected_creation_info, embeddings_model):
    embeddings_model.vectordbs['nodes'].clear()
    embeddings_model.vectordbs['triplets'].clear()

    real_creation_info = embeddings_model.create_triplets(init_triplets, create_nodes=add_nodes_flag)
    assert real_creation_info['nodes'] == expected_creation_info['nodes']
    assert real_creation_info['triplets'] == expected_creation_info['triplets']

    embeddings_model_count = embeddings_model.count_items()
    assert embeddings_model_count['nodes'] == expected_init_count['nodes']
    assert embeddings_model_count['triplets'] == expected_init_count['triplets']

    if add_nodes_flag:
        for node_id in real_creation_info['nodes']:
            assert embeddings_model.vectordbs['nodes'].item_exist(node_id)
        for triplet in init_triplets:
            assert embeddings_model.vectordbs['nodes'].item_exist(triplet.start_node.id)
            assert embeddings_model.vectordbs['nodes'].item_exist(triplet.end_node.id)

    for triplet_id in real_creation_info['triplets']:
        assert embeddings_model.vectordbs['triplets'].item_exist(triplet_id)
    for triplet in init_triplets:
        assert embeddings_model.vectordbs['triplets'].item_exist(triplet.id)


@pytest.mark.parametrize("init_triplets, expected_creation_info, triplets_to_delete, nodes_delete_info, expected_init_count, expected_final_count, embeddings_model", EM_POPULATED_DELETE_TEST_CASES, indirect=['embeddings_model'])
def test_delete_triplets(init_triplets, expected_creation_info, triplets_to_delete, nodes_delete_info, expected_init_count, expected_final_count, embeddings_model):
    embeddings_model.vectordbs['nodes'].clear()
    embeddings_model.vectordbs['triplets'].clear()

    real_creation_info = embeddings_model.create_triplets(init_triplets, create_nodes=True)
    assert real_creation_info['nodes'] == expected_creation_info['nodes']
    assert real_creation_info['triplets'] == expected_creation_info['triplets']

    embeddings_model_count = embeddings_model.count_items()
    assert embeddings_model_count['nodes'] == expected_init_count['nodes']
    assert embeddings_model_count['triplets'] == expected_init_count['triplets']

    embeddings_model.delete_triplets(triplets_to_delete, delete_nodes_info=nodes_delete_info)

    embeddings_model_count = embeddings_model.count_items()
    assert embeddings_model_count['nodes'] == expected_final_count['nodes']
    assert embeddings_model_count['triplets'] == expected_final_count['triplets']

    for triplet, delete_info in zip(triplets_to_delete, nodes_delete_info):
        assert not embeddings_model.vectordbs['triplets'].item_exist(triplet.id)
        if delete_info['s_node']:
            assert not embeddings_model.vectordbs['nodes'].item_exist(triplet.start_node.id)
        if delete_info['e_node']:
            assert not embeddings_model.vectordbs['nodes'].item_exist(triplet.end_node.id)
