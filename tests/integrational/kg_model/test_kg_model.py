from .cases import KG_POPULATED_CREATE_TEST_CASES, KG_POPULATED_DELETE_TEST_CASES, KG_POPULATED_CLEAR_TEST_CASES
from src.utils import Triplet
from src.kg_model import KnowledgeGraphModel
import pytest
from typing import List, Dict, Union
from functools import reduce

import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.utils.data_structs import RelationType, NodeType

@pytest.mark.parametrize("triplets, expected_count, expected_graph_cinfo, expected_vector_cinfo, kg_model", KG_POPULATED_CREATE_TEST_CASES, indirect=['kg_model'])
def test_add_knowledge(triplets: List[Triplet], expected_count: Dict[str, Dict[str, int]],
                       expected_graph_cinfo: Dict[str, Dict[Union[NodeType, RelationType], List[str]]], expected_vector_cinfo: Dict[str, List[str]],
                       kg_model: KnowledgeGraphModel):
    kg_model.clear()

    real_create_info = kg_model.add_knowledge(triplets)

    #
    assert real_create_info['graph_info'].keys() == expected_graph_cinfo.keys()
    for n_type, real_nids in real_create_info['graph_info']['nodes'].items():
        assert expected_graph_cinfo['nodes'].get(n_type, set()) == real_nids
    for r_type, real_tids in real_create_info['graph_info']['triplets'].items():
        assert expected_graph_cinfo['triplets'].get(r_type, set()) == real_tids

    #
    assert real_create_info['embeddings_info'].keys() == expected_vector_cinfo.keys()
    for expexted_k, expected_val in expected_vector_cinfo.items():
        if expexted_k == 'nodes':
            real_val = reduce(lambda acc, val: acc.union(val), list(real_create_info['embeddings_info'][expexted_k].values()), set())
            assert  real_val == set(expected_val)
        elif expexted_k == 'triplets':
            assert real_create_info['embeddings_info'][expexted_k] == set(expected_val)
        else:
            raise KeyError


    real_count = kg_model.count_items()
    assert real_count['graph_info']['nodes'] == expected_count['graph_info']['nodes']
    assert real_count['graph_info']['triplets'] == expected_count['graph_info']['triplets']
    assert real_count['embeddings_info']['nodes'] == expected_count['embeddings_info']['nodes']
    assert real_count['embeddings_info']['triplets'] == expected_count['embeddings_info']['triplets']
    assert real_count['nodestree_info'] == expected_count['nodestree_info']


@pytest.mark.parametrize("init_triplets, expected_init_count, delete_triplets, expected_final_count, expected_graph_dinfo, expected_vector_dinfo, kg_model", KG_POPULATED_DELETE_TEST_CASES, indirect=['kg_model'])
def test_remove_knowledge(init_triplets: List[Triplet], expected_init_count: Dict[str, Dict[str, int]],
                          delete_triplets: List[Triplet], expected_final_count: Dict[str, Dict[str, int]],
                          expected_graph_dinfo: Dict[int, Dict[str, bool]], expected_vector_dinfo: Dict[int, Dict[str, bool]],
                          kg_model: KnowledgeGraphModel):
    kg_model.clear()

    _ = kg_model.add_knowledge(init_triplets)
    assert kg_model.count_items() == expected_init_count

    real_delete_info = kg_model.remove_knowledge(delete_triplets)
    assert real_delete_info['graph_info'] == expected_graph_dinfo
    for triplet_idx, real_delete_tinfo in real_delete_info['graph_info'].items():
        for node_name, delete_flag in real_delete_tinfo.items():
            assert expected_graph_dinfo[triplet_idx][node_name] == delete_flag

    assert real_delete_info['embeddings_info'] == expected_vector_dinfo
    for triplet_idx, real_delete_tinfo in real_delete_info['embeddings_info'].items():
        for node_name, delete_flag in real_delete_tinfo.items():
            assert expected_vector_dinfo[triplet_idx][node_name] == delete_flag

    real_count = kg_model.count_items()
    assert real_count['graph_info']['nodes'] == expected_final_count['graph_info']['nodes']
    assert real_count['graph_info']['triplets'] == expected_final_count['graph_info']['triplets']
    assert real_count['embeddings_info']['nodes'] == expected_final_count['embeddings_info']['nodes']
    assert real_count['embeddings_info']['triplets'] == expected_final_count['embeddings_info']['triplets']
    assert real_count['nodestree_info'] == expected_final_count['nodestree_info']


@pytest.mark.parametrize("init_triplets, expected_init_count, kg_model", KG_POPULATED_CLEAR_TEST_CASES, indirect=['kg_model'])
def test_clear(init_triplets: List[Triplet], expected_init_count: Dict[str, Dict[str, int]], kg_model: KnowledgeGraphModel):
    kg_model.clear()
    _ = kg_model.add_knowledge(init_triplets)

    real_count = kg_model.count_items()
    assert real_count['graph_info']['nodes'] == expected_init_count['graph_info']['nodes']
    assert real_count['graph_info']['triplets'] == expected_init_count['graph_info']['triplets']
    assert real_count['embeddings_info']['nodes'] == expected_init_count['embeddings_info']['nodes']
    assert real_count['embeddings_info']['triplets'] == expected_init_count['embeddings_info']['triplets']
    assert real_count['nodestree_info'] == None

    kg_model.clear()
    real_count = kg_model.count_items()
    assert real_count['graph_info']['nodes'] == 0
    assert real_count['graph_info']['triplets'] == 0
    assert real_count['embeddings_info']['nodes'] == 0
    assert real_count['embeddings_info']['triplets'] == 0
    assert real_count['nodestree_info'] == None
