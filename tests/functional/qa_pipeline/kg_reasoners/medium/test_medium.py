import pytest
from typing import List, Dict
from tqdm import tqdm
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
sys.path.insert(0, PROJECT_BASE_DIR)


from src.pipelines.qa.kg_reasoning.medium_reasoner import MediumKGReasoner, MediumKGReasonerConfig
from src.kg_model import KnowledgeGraphModel
from .cases import POPULATED_MEDIUM_REASONER_TEST_CASES

@pytest.mark.parametrize("reasoner_config, query, kg_model", POPULATED_MEDIUM_REASONER_TEST_CASES, indirect=['kg_model'])
def test_medium_reasoner(reasoner_config: MediumKGReasonerConfig, query: str, kg_model: KnowledgeGraphModel):
    reasoner = MediumKGReasoner(kg_model, reasoner_config, kg_model.cache_config)

    _, info, _ = reasoner.perform(query)
    assert info.status.value == 0
