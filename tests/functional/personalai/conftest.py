import pytest
import sys
from copy import deepcopy
from typing import Dict
from itertools import product
import os, shutil
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
BASE_TESTS_OUTPUT_DIR = "functional/personalai/tests_output"
sys.path.insert(0, PROJECT_BASE_DIR)

from src import PersonalAI, PersonalAIConfig
from src.utils.agent_stat_analyzer import AgentStatAnalyzerConfig
from src.utils.data_structs import create_id

from .cases import RAW_TEXTS, AVAILABLE_LANGUAGES, AVAILABLE_PAICONFIG_COMBINATIONS, \
    AVAILABLE_CACHE_DBS, AVAILABLE_AGENTSTAT_DBS

from .available_personalai_configs import *
from ...integrational.utils.agent_stat_analyzer.available_agentstatanalyzer_configs import *
from ...integrational.db_drivers.kv_driver.available_kv_configs import *

def clear_tests_output():
    for filename in os.listdir(BASE_TESTS_OUTPUT_DIR ):
        file_path = os.path.join(BASE_TESTS_OUTPUT_DIR , filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

@pytest.fixture(scope='module')
def available_personaai_instances(
    available_personalai_configs, available_kv_configs, 
    available_agentstatanalyzer_configs):

    extended_pai_vendors = list(product(
        AVAILABLE_PAICONFIG_COMBINATIONS, AVAILABLE_CACHE_DBS, 
        AVAILABLE_AGENTSTAT_DBS))

    pai_instances: Dict[str, PersonalAI] = dict()
    for language in AVAILABLE_LANGUAGES:
        for cur_pai_vendors in extended_pai_vendors:
            kw_pai, kw_cache, kw_agentstat = "/".join(cur_pai_vendors[0]), \
                cur_pai_vendors[1], cur_pai_vendors[2]

            #
            config: PersonalAIConfig = deepcopy(available_personalai_configs[kw_pai])
            config.lang = language
            config.pai_name = None
            config.pai_name = f"personalai_env_{create_id()[:5]}"
            config.pai_base_path = BASE_TESTS_OUTPUT_DIR
            config.log_base_path = BASE_TESTS_OUTPUT_DIR
            config.kg_model_config.graph_struct_config.driver_config.db_config.db_info['table'] += language
            for nodes_vstruct_config in config.kg_model_config.graph_embeddings_config.nodesdb_driver_configs_mapping.values():
                nodes_vstruct_config.db_config.db_info['table'] += language
            for triplets_vstruct_config in config.kg_model_config.graph_embeddings_config.tripletsdb_driver_configs_mapping.values():
                triplets_vstruct_config.db_config.db_info['table'] += language

            #
            kv_cache_config = None
            if kw_cache != "None":
                kv_cache_config: KeyValueDriverConfig = deepcopy(available_kv_configs[kw_cache])
                kv_cache_config.db_config.db_info['db'] += language
                kv_cache_config.db_config.need_to_clear = False

            #
            stat_config = None 
            if kw_agentstat != "None":
                stat_config: AgentStatAnalyzerConfig = deepcopy(available_agentstatanalyzer_configs[kw_agentstat])
                stat_config.table_driver_config.db_config.db_info['db'] += language
                config.textidstore_config.texttotriplets_store_config.db_config.db_info['db'] += language
                config.textidstore_config.triplettotexts_store_config.db_config.db_info['db'] += language
                stat_config.table_driver_config.db_config.need_to_clear = False

            #
            kw_paiinst = '|'.join([kw_pai,kw_cache,kw_agentstat,language])
            pai_instances[kw_paiinst] = PersonalAI(config, kv_cache_config, stat_config)
            pai_instances[kw_paiinst].open_connections()
            pai_instances[kw_paiinst].kg_model.clear()
            pai_instances[kw_paiinst].textid_store.clear_store()
            
    return pai_instances

@pytest.fixture(scope='module')
def notempty_pai_instances(available_personaai_instances: Dict[str, PersonalAI]):
    for kw_paiinst, pai_inst in available_personaai_instances.items():
        pai_inst.kg_model.clear()
        pai_inst.textid_store.clear_store()

        language = kw_paiinst.split("|")[-1]
        for text in RAW_TEXTS[language]:
            pai_inst.update_memory(text)
        pai_inst.kg_model.check_consistency()
    return available_personaai_instances

@pytest.fixture(scope='function')
def personal_ai(notempty_pai_instances, request):
    return notempty_pai_instances[request.param]
