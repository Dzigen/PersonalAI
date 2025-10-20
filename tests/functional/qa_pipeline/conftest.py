import pytest
import sys
from copy import deepcopy
from typing import Dict
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.kg_model import KnowledgeGraphModelConfig, KnowledgeGraphModel
from src.pipelines.memorize import MemPipeline
from src.config import DEFAULT_PERSONALAI_KVCACHE_CONFIG

from .cases import RAW_TEXTS


@pytest.fixture(scope='package')
def en_kg_model(request):
    config = KnowledgeGraphModelConfig()
    config.graph_struct_config.driver_config.db_config.db_info['table'] += 'EN'
    for nodes_vstruct_config in config.graph_embeddings_config.nodesdb_driver_configs_mapping.values():
        nodes_vstruct_config.db_config.db_info['table'] += 'EN'
    for triplets_vstruct_config in config.graph_embeddings_config.tripletsdb_driver_configs_mapping.values():
        triplets_vstruct_config.db_config.db_info['table'] += 'EN'

    cache_config = deepcopy(DEFAULT_PERSONALAI_KVCACHE_CONFIG)
    cache_config.db_config.db_info['db'] += 'EN'

    kg_model = KnowledgeGraphModel(config, cache_config)
    kg_model.clear()
    mem_pipeline = MemPipeline(kg_model, cache_kvdriver_config=cache_config)

    for text in RAW_TEXTS['en']:
        mem_pipeline.remember(text)
    kg_model.check_consistency()

    return kg_model

@pytest.fixture(scope='package')
def ru_kg_model(request):
    config = KnowledgeGraphModelConfig()
    config.graph_struct_config.driver_config.db_config.db_info['table'] += 'RU'
    for nodes_vstruct_config in config.graph_embeddings_config.nodesdb_driver_configs_mapping.values():
        nodes_vstruct_config.db_config.db_info['table'] += 'RU'
    for triplets_vstruct_config in config.graph_embeddings_config.tripletsdb_driver_configs_mapping.values():
        triplets_vstruct_config.db_config.db_info['table'] += 'RU'

    cache_config = deepcopy(DEFAULT_PERSONALAI_KVCACHE_CONFIG)
    cache_config.db_config.db_info['db'] += 'RU'

    kg_model = KnowledgeGraphModel(config, cache_config)
    kg_model.clear()
    mem_pipeline = MemPipeline(kg_model, cache_kvdriver_config=cache_config)

    for text in RAW_TEXTS['ru']:
        mem_pipeline.remember(text)
    kg_model.check_consistency()

    return kg_model

@pytest.fixture(scope='package')
def available_kg_model(ru_kg_model, en_kg_model):
    return {
        'ru': ru_kg_model,
        'en': en_kg_model
    }

@pytest.fixture(scope='function')
def kg_model(available_kg_model, request):
    return available_kg_model[request.param]
