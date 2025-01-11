import pytest
from typing import List, Dict

import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.kg_model import KnowledgeGraphModel
from src.utils import Triplet

from cases import KG_POPULATED_CREATE_TEST_CASES, KG_POPULATED_DELETE_TEST_CASES, KG_POPULATED_CLEAR_TEST_CASES

@pytest.mark.parametrize("triplets, expected_count, expected_graph_cinfo, expected_vector_cinfo, kg_model", KG_POPULATED_CREATE_TEST_CASES, indirect=['kg_model'])
def test_add_knowledge(triplets: List[Triplet], expected_count: Dict[str, Dict[str, int]],
                       expected_graph_cinfo: Dict[str,List[str]], expected_vector_cinfo: Dict[str, List[str]],
                       kg_model: KnowledgeGraphModel):
    kg_model.clear()

    real_create_info = kg_model.add_knowledge(triplets)
    real_count = kg_model.count_items()
    assert real_count['graph_info'] == expected_count['graph_info']
    assert real_count['embeddings_info'] == expected_count['embeddings_info']

    assert real_create_info['graph_info'] == expected_graph_cinfo
    assert real_create_info['embeddings_info'] == expected_vector_cinfo

@pytest.mark.parametrize("init_triplets, expected_init_count, delete_triplets, expected_final_count, expected_graph_dinfo, expected_vector_dinfo, kg_model", KG_POPULATED_DELETE_TEST_CASES, indirect=['kg_model'])
def test_remove_knowledge(init_triplets: List[Triplet], expected_init_count: Dict[str, Dict[str, int]],
                          delete_triplets: List[Triplet], expected_final_count: Dict[str, Dict[str, int]],
                          expected_graph_dinfo: Dict[int,Dict[str,bool]], expected_vector_dinfo: Dict[int,Dict[str,bool]],
                          kg_model: KnowledgeGraphModel):
    kg_model.clear()

    _ = kg_model.add_knowledge(init_triplets)
    assert kg_model.count_items() == expected_init_count

    real_delete_info = kg_model.remove_knowledge(delete_triplets)

    assert kg_model.count_items() == expected_final_count
    assert real_delete_info['graph_info'] == expected_graph_dinfo
    assert real_delete_info['embeddings_info'] == expected_vector_dinfo


@pytest.mark.parametrize("init_triplets, expected_init_count, kg_model", KG_POPULATED_CLEAR_TEST_CASES, indirect=['kg_model'])
def test_clear(init_triplets: List[Triplet], expected_init_count: Dict[str, Dict[str,int]], kg_model: KnowledgeGraphModel):
    kg_model.clear()
    _ = kg_model.add_knowledge(init_triplets)

    real_count = kg_model.count_items()
    assert real_count['graph_info'] == expected_init_count['graph_info']
    assert real_count['embeddings_info'] == expected_init_count['embeddings_info']

    kg_model.clear()
    assert kg_model.count_items() == {'graph_info': {'nodes': 0, 'triplets': 0}, 'embeddings_info': {'nodes': 0, 'triplets': 0}}
