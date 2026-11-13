import pytest
import sys
from typing import Dict
from copy import deepcopy
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.TextIdStore import TextIdStoreConfig

from ..db_drivers.kv_driver.available_kv_configs import *

@pytest.fixture(scope='session')
def available_textidstore_configs(available_kv_configs):
    configs: Dict[str, TextIdStoreConfig] = dict()
    for kvdb_vendor, kvdb_config in available_kv_configs.items():
        configs[kvdb_vendor] = TextIdStoreConfig(
            texttotriplets_store_config=deepcopy(kvdb_config),
            triplettotexts_store_config=deepcopy(kvdb_config),
            log_base_path=TEST_VOLUME_DIR
        )
        configs[kvdb_vendor].texttotriplets_store_config.db_config.db_info['table'] = 'texttotriplets_store'
        configs[kvdb_vendor].triplettotexts_store_config.db_config.db_info['table'] = 'triplettotexts_store'

    return configs