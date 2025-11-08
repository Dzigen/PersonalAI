import pytest
import sys
from copy import deepcopy
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src import PersonalAI, PersonalAIConfig
from src.config import DEFAULT_PERSONALAI_KVCACHE_CONFIG
from src.utils.agent_stat_analyzer import AgentStatAnalyzerConfig

from .cases import RAW_TEXTS_EN, RAW_TEXTS_RU

@pytest.fixture(scope='package')
def personaai_ru():
    config = PersonalAIConfig()
    config.kg_model_config.graph_struct_config.driver_config.db_config.db_info['table'] += 'RU'
    for nodes_vstruct_config in config.kg_model_config.graph_embeddings_config.nodesdb_driver_configs_mapping.values():
        nodes_vstruct_config.db_config.db_info['table'] += 'RU'
    for triplets_vstruct_config in config.kg_model_config.graph_embeddings_config.tripletsdb_driver_configs_mapping.values():
        triplets_vstruct_config.db_config.db_info['table'] += 'RU'

    kv_cache_config = deepcopy(DEFAULT_PERSONALAI_KVCACHE_CONFIG)
    kv_cache_config.db_config.db_info['db'] += 'RU'

    stat_config = AgentStatAnalyzerConfig()
    stat_config.table_driver_config.db_config.db_info['db'] += 'RU'

    personal_ai = PersonalAI(config, kv_cache_config, stat_config)
    personal_ai.kg_model.clear()
    for text in RAW_TEXTS_RU:
        personal_ai.update_memory(text)
    personal_ai.kg_model.check_consistency()

    # def finalizer():
    #     personal_ai.kg_model.clear()
    #     personal_ai.mem_pipeline.clear_agent_tgen_stat()
    #     personal_ai.mem_pipeline.clear_kv_caches()
    #     personal_ai.qa_pipeline.clear_agent_tgen_stat()
    #     personal_ai.qa_pipeline.clear_kv_caches()
    # request.addfinalizer(finalizer)

    return personal_ai

@pytest.fixture(scope='package')
def personaai_en():
    config = PersonalAIConfig()
    config.kg_model_config.graph_struct_config.driver_config.db_config.db_info['table'] += 'EN'
    for nodes_vstruct_config in config.kg_model_config.graph_embeddings_config.nodesdb_driver_configs_mapping.values():
        nodes_vstruct_config.db_config.db_info['table'] += 'EN'
    for triplets_vstruct_config in config.kg_model_config.graph_embeddings_config.tripletsdb_driver_configs_mapping.values():
        triplets_vstruct_config.db_config.db_info['table'] += 'EN'

    kv_cache_config = deepcopy(DEFAULT_PERSONALAI_KVCACHE_CONFIG)
    kv_cache_config.db_config.db_info['db'] += 'EN'

    stat_config = AgentStatAnalyzerConfig()
    stat_config.table_driver_config.db_config.db_info['db'] += 'EN'

    personal_ai = PersonalAI(config, kv_cache_config, stat_config)
    personal_ai.kg_model.clear()
    for text in RAW_TEXTS_EN:
        personal_ai.update_memory(text)
    personal_ai.kg_model.check_consistency()

    # def finalizer():
    #     personal_ai.kg_model.clear()
    #     personal_ai.mem_pipeline.clear_agent_tgen_stat()
    #     personal_ai.mem_pipeline.clear_kv_caches()
    #     personal_ai.qa_pipeline.clear_agent_tgen_stat()
    #     personal_ai.qa_pipeline.clear_kv_caches()
    # request.addfinalizer(finalizer)

    return personal_ai

@pytest.fixture(scope='package')
def available_personaai_instances(personaai_ru, personaai_en):
    return {
        'ru': personaai_ru,
        'en': personaai_en
    }


@pytest.fixture(scope='function')
def personal_ai(available_personaai_instances, request):
    return available_personaai_instances[request.param]
