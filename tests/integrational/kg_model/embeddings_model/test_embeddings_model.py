import pytest
from typing import Dict, List, Set
from functools import reduce
import sys
sys.path.insert(0, "../")

from .cases import EM_POPULATED_CREATE_TEST_CASES, EM_POPULATED_DELETE_TEST_CASES
from src.kg_model import EmbeddingsModel
from src.utils import Triplet

@pytest.mark.parametrize("init_triplets, add_nodes_flag, expected_init_count, expected_creation_info, embeddings_model", EM_POPULATED_CREATE_TEST_CASES, indirect=['embeddings_model'])
def test_create_triplets(init_triplets: List[Triplet], add_nodes_flag: bool, expected_init_count: Dict[str, int],
                         expected_creation_info: Dict[str, Set[str]], embeddings_model: EmbeddingsModel):
    embeddings_model.clear()
    real_creation_info = embeddings_model.create_triplets(init_triplets, create_nodes=add_nodes_flag)

    #
    print(real_creation_info)
    assert real_creation_info.keys() == expected_creation_info.keys()
    for expexted_k, expected_val in expected_creation_info.items():
        if expexted_k == 'nodes':
            real_val = reduce(lambda acc, val: acc.union(val), list(real_creation_info[expexted_k].values()), set())
            assert  real_val == expected_val
        elif expexted_k == 'triplets':
            assert real_creation_info[expexted_k] == expected_val
        else:
            raise KeyError
    #
    embeddings_model_count = embeddings_model.count_items()
    print(embeddings_model_count)
    assert embeddings_model_count.keys() == expected_init_count.keys()
    for expexted_k, expected_val in expected_init_count.items():
        assert embeddings_model_count[expexted_k] == expected_val

    if add_nodes_flag:
        for node_type, node_ids in real_creation_info['nodes'].items():
            for node_id in node_ids:
                assert embeddings_model.nodes_vcomposers[node_type].item_exist(node_id)
        for triplet in init_triplets:
            assert embeddings_model.nodes_vcomposers[triplet.start_node.type].item_exist(triplet.start_node.id)
            assert embeddings_model.nodes_vcomposers[triplet.end_node.type].item_exist(triplet.end_node.id)

    for triplet_id in real_creation_info['triplets']:
        assert embeddings_model.triplets_vcomposer.item_exist(triplet_id)
    for triplet in init_triplets:
        assert embeddings_model.triplets_vcomposer.item_exist(triplet.relation.id)

    embeddings_model.clear()


@pytest.mark.parametrize("init_triplets, expected_creation_info, expected_init_count, triplets_to_delete, delete_info, expected_final_count, exception, embeddings_model", EM_POPULATED_DELETE_TEST_CASES, indirect=['embeddings_model'])
def test_delete_triplets(init_triplets: List[Triplet], expected_creation_info: Dict[str, Set[str]], expected_init_count: Dict[str, int],
                         triplets_to_delete: List[Triplet], delete_info: Dict[int, Dict[str, bool]], expected_final_count: Dict[str, int],
                         exception: bool, embeddings_model: EmbeddingsModel):
    embeddings_model.clear()

    real_creation_info = embeddings_model.create_triplets(init_triplets, create_nodes=True)

    #
    print(real_creation_info)
    assert real_creation_info.keys() == expected_creation_info.keys()
    for expexted_k, expected_val in expected_creation_info.items():
        if expexted_k == 'nodes':
            real_val = reduce(lambda acc, val: acc.union(val), list(real_creation_info[expexted_k].values()), set())
            assert  real_val == expected_val
        elif expexted_k == 'triplets':
            assert real_creation_info[expexted_k] == expected_val
        else:
            raise KeyError

    #
    embeddings_model_count = embeddings_model.count_items()
    assert embeddings_model_count.keys() == expected_init_count.keys()
    for expexted_k, expected_val in expected_init_count.items():
        assert embeddings_model_count[expexted_k] == expected_val

    flag = False
    try:
        embeddings_model.delete_triplets(triplets_to_delete, delete_info=delete_info)
    except AssertionError:
        assert exception
        flag = True

    if not exception:
        embeddings_model_count = embeddings_model.count_items()

        #
        assert embeddings_model_count.keys() == expected_final_count.keys()
        for expexted_k, expected_val in expected_final_count.items():
            assert embeddings_model_count[expexted_k] == expected_val

        #
        for i, triplet in enumerate(triplets_to_delete):
            if delete_info[i]['triplet']:
                assert not embeddings_model.triplets_vcomposer.item_exist(triplet.relation.id)
            if delete_info[i]['s_node']:
                assert not embeddings_model.nodes_vcomposers[triplet.start_node.type].item_exist(triplet.start_node.id)
            if delete_info[i]['e_node']:
                assert not embeddings_model.nodes_vcomposers[triplet.end_node.type].item_exist(triplet.end_node.id)
    else:
        if not flag:
            assert False

    embeddings_model.clear()
