import pytest
from typing import List, Dict
from tqdm import tqdm
import sys
import flatdict

# TO CHANGE
PROJECT_BASE_DIR = '../'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.kg_model import KnowledgeGraphModel
from src.pipelines.memorize import MemPipeline, MemPipelineConfig
from .cases import KV_CACHE_CONFIG, MEM_POPULATED_TEST_CASES

def assert_kgmodel_count(kg_model: KnowledgeGraphModel, func):
    count = kg_model.count_items(detailed=True)
    print(count)
    real_counts = dict(flatdict.FlatDict(count, delimiter='.'))
    for c_name, c_value in real_counts.items():
        if kg_model.nodestree_model is None and c_name.startswith('nodestree_info'):
            continue
        else:
            if c_name.endswith('root'):
                assert c_value == 1
            else:
                assert func(c_value,0)

def assert_cache_count(mem_pipeline: MemPipeline, func):
    count = mem_pipeline.get_cache_stat()
    print(count)
    real_counts = dict(flatdict.FlatDict(count, delimiter='.'))
    for c_name, c_value in real_counts.items():
        if c_name.startswith("updator"):
            assert c_value in [None, 0]
        assert func(c_value, 0)

@pytest.mark.parametrize("mem_config, raw_texts, use_kv_cache, clear_kv_cache, kg_model", MEM_POPULATED_TEST_CASES, indirect=['kg_model'])
def test_mem_pipeline(mem_config: MemPipelineConfig, raw_texts: List[str],
                      use_kv_cache: bool, clear_kv_cache: bool, kg_model: KnowledgeGraphModel):
    kg_model.clear()
    assert_kgmodel_count(kg_model, lambda a,b: a == b)
    kg_model.check_consistency()

    kv_cache_config = None
    if use_kv_cache:
        kv_cache_config = KV_CACHE_CONFIG
    mem_pipeline = MemPipeline(kg_model, mem_config, kv_cache_config)

    for text in tqdm(raw_texts):
        _, status = mem_pipeline.remember(text)
        assert status.status.value == 0
    kg_model.check_consistency()

    assert_kgmodel_count(kg_model, lambda a,b: a > b)
    if use_kv_cache:
        assert_cache_count(mem_pipeline, lambda a,b: (a is None) or (a > b))

    if use_kv_cache and clear_kv_cache:
        mem_pipeline.clear_kv_caches()
        assert_cache_count(mem_pipeline, lambda a,b: (a is None) or (a == b))

    kg_model.clear()
