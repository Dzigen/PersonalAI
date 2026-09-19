import pytest
from typing import List, Dict
from tqdm import tqdm
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.pipelines.qa.knowledge_retriever import KnowledgeRetriever, KnowledgeRetrieverConfig
from src.pipelines.qa.kg_reasoning.weak_reasoner.knowledge_comparator import KnowledgeComparator
from src.pipelines.qa.knowledge_retriever.utils import AbstractTriplesFilter, AbstractTripletsRetriever
from src.kg_model import KnowledgeGraphModel
from src.utils.data_structs import QueryInfo

from .cases import POPULATES_KG_TRAVERSE_TEST_CASES

@pytest.mark.parametrize("traversal_name, traversal_config, filter_name, filter_config, query, entities, kg_model",
                         POPULATES_KG_TRAVERSE_TEST_CASES, indirect=['kg_model'])
def test_knowledge_retriever(
    traversal_name: str, traversal_config: AbstractTriplesFilter,
    filter_name: str, filter_config: AbstractTripletsRetriever,
    query: str, entities: List[str], kg_model: KnowledgeGraphModel):

    kr_config = KnowledgeRetrieverConfig(
        retriever_method=traversal_name, retriever_config=traversal_config,
        filter_method=filter_name, filter_config=filter_config
    )

    comparator_stage = KnowledgeComparator(kg_model)
    retriever_stage = KnowledgeRetriever(
        kg_model=kg_model, config=kr_config,
        cache_kvdriver_config=kg_model.cache_config
    )

    q_info = QueryInfo(query=query, entities=entities)
    linking_result, rinfo, _ = comparator_stage.perform(q_info)
    linked_nodes, linked_nodes_by_entities = linking_result
    assert rinfo.status.value == 0
    q_info.linked_nodes = linked_nodes
    q_info.linked_nodes_by_entities = linked_nodes_by_entities

    _, info, _ = retriever_stage.retrieve(q_info)
    assert info.status.value == 0
