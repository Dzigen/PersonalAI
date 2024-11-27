import pytest

import sys
sys.path.insert(0, "../../")

from src.utils import Triplet
from src.pipelines.memorize import LLMUpdator

from typing import List, Dict

@pytest.mark.parametrize("triplets, delete_obsolete_info, need_simple, need_hyper, need_episodic", [
    # TODO
])
def test_update_knowledge(llm_updator: LLMUpdator, triplets: List[Triplet], delete_obsolete_info:bool,
                          need_simple:bool, need_hyper:bool, need_episodic:bool):
    # TODO
    pass
