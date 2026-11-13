import pytest
import sys
from copy import deepcopy
from typing import Dict
import os, shutil
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
BASE_TESTS_OUTPUT_DIR = "functional/personalai/tests_output"
sys.path.insert(0, PROJECT_BASE_DIR)

from src import PersonalAIConfig

from ...integrational.kg_model.available_kgmodel_configs import *
from ...integrational.db_drivers.kv_driver.available_kv_configs import *
from ...integrational.utils.agent_stat_analyzer.available_agentstatanalyzer_configs import *
from ...integrational.textid_store.available_textidstore_configs import *

@pytest.fixture(scope='session')
def available_personalai_configs(
    available_kgmodel_configs, available_textidstore_configs
):
    pai_configs: Dict[str, PersonalAIConfig] = dict()
    for kg_vendor, kg_config in available_kgmodel_configs.items():
        for tid_vendor, tid_config in available_textidstore_configs.items():
            kw_config = f"{kg_vendor}/{tid_vendor}"
            pai_configs[kw_config] = PersonalAIConfig(
                kg_model_config=deepcopy(kg_config),
                textidstore_config=deepcopy(tid_config),
                log_base_path=None,
                pai_base_path=BASE_TESTS_OUTPUT_DIR
            )

            # костыль
            pai_configs[kw_config].textidstore_config.texttotriplets_store_config.db_config.need_to_clear = False
            pai_configs[kw_config].textidstore_config.triplettotexts_store_config.db_config.need_to_clear = False
            pai_configs[kw_config].kg_model_config.graph_struct_config.driver_config.db_config.need_to_clear = False
            pai_configs[kw_config].kg_model_config.graph_embeddings_config.nodesdb_driver_configs_mapping['dense_nodes'].db_config.need_to_clear = False
            pai_configs[kw_config].kg_model_config.graph_embeddings_config.nodesdb_driver_configs_mapping['bm25_nodes'].db_config.need_to_clear = False
            pai_configs[kw_config].kg_model_config.graph_embeddings_config.tripletsdb_driver_configs_mapping['dense_triplets'].db_config.need_to_clear = False
            pai_configs[kw_config].kg_model_config.graph_embeddings_config.tripletsdb_driver_configs_mapping['bm25_triplets'].db_config.need_to_clear = False

            pai_configs[kw_config].synchronize_environment()
            pai_configs[kw_config].synchronize_logging()

    return pai_configs