import pytest
from typing import List, Dict

import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.kg_model import KnowledgeGraphModel
from src.utils import Triplet

from cases import KG_POPULATED_CREATE_TEST_CASES, KG_POPULATED_DELETE_TEST_CASES

@pytest.mark.parametrize("triplets, expected_count, expected_graph_ids, expected_vector_ids, kg_model", KG_POPULATED_CREATE_TEST_CASES, indirect=['kg_model'])
def test_add_knowledge(triplets: List[Triplet], expected_count: Dict[str, Dict[str, int]],
                       expected_graph_ids: Dict[str,List[str]], expected_vector_ids: Dict[str, List[str]], kg_model: KnowledgeGraphModel):
    # TODO
    pass

@pytest.mark.parametrize("init_triplets, expected_init_count, delete_triplets, expected_graph_ids, expected_vector_ids, kg_model", KG_POPULATED_DELETE_TEST_CASES, indirect=['kg_model'])
def test_remove_knowledge(init_triplets: List[Triplet], expected_init_count: Dict[str, Dict[str, int]], delete_triplets: List[Triplet],
                          expected_graph_ids: Dict[str, List[str]], expected_vector_ids: Dict[str, List[str]], kg_model: KnowledgeGraphModel):
    # TODO
    pass

def test_clear(init_tripelets: List[Triplet], expected_init_count: Dict[str, Dict[str,int]]):
    # TODO
    pass
