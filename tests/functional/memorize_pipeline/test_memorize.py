import pytest
from typing import List, Dict
from tqdm import tqdm
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.kg_model import KnowledgeGraphModel
from src.pipelines.memorize import MemPipeline, MemPipelineConfig
from .cases import KV_CACHE_CONFIG, MEM_POPULATED_TEST_CASES

@pytest.mark.parametrize("mem_config, raw_texts, use_kv_cache, clear_kv_cache, kg_model", MEM_POPULATED_TEST_CASES, indirect=['kg_model'])
def test_mem_pipeline(mem_config: MemPipelineConfig, raw_texts: List[str],
                      use_kv_cache: bool, clear_kv_cache: bool, kg_model: KnowledgeGraphModel):
    kg_model.clear()

    g_items_count = kg_model.graph_struct.count_items()
    assert g_items_count['triplets'] == 0
    assert g_items_count['nodes'] == 0
    e_items_count = kg_model.graph_embeddings.count_items()
    assert e_items_count['nodes'] == 0
    assert e_items_count['triplets'] == 0

    kv_cache_config = None
    if use_kv_cache:
        kv_cache_config = KV_CACHE_CONFIG
    mem_pipeline = MemPipeline(kg_model, mem_config, kv_cache_config)

    for text in tqdm(raw_texts):
        _, status = mem_pipeline.remember(text)
        assert status.status.value == 0

    if use_kv_cache and clear_kv_cache:
        mem_pipeline.clear_kv_caches()

    kg_model.clear()
