import pytest
import sys
from copy import deepcopy
from typing import Dict
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.kg_model import KnowledgeGraphModelConfig, KnowledgeGraphModel
from src.pipelines.memorize import MemPipeline, MemPipelineConfig
from src.config import DEFAULT_PERSONALAI_KVCACHE_CONFIG

from .cases import RAW_TEXTS, AVAILABLE_LANGUAGES

@pytest.fixture(scope='package')
def available_kg_models():
    kg_models: Dict[str, KnowledgeGraphModel] = dict()
    for lang in AVAILABLE_LANGUAGES:
        kg_config = KnowledgeGraphModelConfig(
            pai_base_path=TEST_VOLUME_DIR, 
            log_base_path=TEST_VOLUME_DIR
        )
        kg_config.synchronize_logging()
        kg_config.synchronize_environment()
        kg_config.synchronize_database()

        kg_config.graph_struct_config.driver_config.db_config.db_info['table'] += lang
        for nodes_vstruct_config in kg_config.graph_embeddings_config.nodesdb_driver_configs_mapping.values():
            nodes_vstruct_config.db_config.db_info['table'] += lang
        for triplets_vstruct_config in kg_config.graph_embeddings_config.tripletsdb_driver_configs_mapping.values():
            triplets_vstruct_config.db_config.db_info['table'] += lang

        cache_config = deepcopy(DEFAULT_PERSONALAI_KVCACHE_CONFIG)
        cache_config.db_config.db_info['db'] += lang
        cache_config.db_config.db_info['expected_db_base_path'] = TEST_VOLUME_DIR

        kg_models[lang] = KnowledgeGraphModel(kg_config, cache_config)
        kg_models[lang].open_connections()
        kg_models[lang].clear()

        mempipeline_config = MemPipelineConfig(
            lang=lang,
            log_base_path=TEST_VOLUME_DIR
        )
        mempipeline_config.synchronize_logging()
        mempipeline_config.synchronize_language()

        mem_pipeline = MemPipeline(kg_models[lang], mempipeline_config,cache_config)
        mem_pipeline.open_connections()
        for text in RAW_TEXTS[lang]:
            mem_pipeline.remember(text)
        mem_pipeline.close_connections()

        kg_models[lang].check_consistency()
    return kg_models

@pytest.fixture(scope='function')
def kg_model(available_kg_models, request):
    return available_kg_models[request.param]
