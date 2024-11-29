import pytest

import sys
sys.path.insert(0, "../")

from src.utils import Triplet
from src.pipelines.memorize import LLMUpdator

from typing import List, Dict

@pytest.mark.parametrize("triplets, delete_obsolete_info, need_simple, need_hyper,\
                          need_episodic, agent_stub_answers, expected_status,\
                          expected_graphdb_triplet_ids, expected_vectordb_triplet_ids, expected_vectordb_node_ids", [
    # TODO
])
def test_update_knowledge(llm_updator: LLMUpdator, triplets: List[Triplet], delete_obsolete_info:bool,
                          need_simple:bool, need_hyper:bool, need_episodic:bool, agent_stub_answers: List[str],
                          expected_graphdb_triplet_ids: List[str], expected_vectordb_triplet_ids: List[str],
                          expected_vectordb_node_ids: List[str]):
    # TODO
    pass
