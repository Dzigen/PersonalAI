import pytest
import sys
from copy import deepcopy
from typing import Dict
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.db_drivers.kv_driver import KeyValueDriver, KeyValueDriverConfig, KVDBConnectionConfig
from src.TextIdStore import TextIdStore, TextIdStoreConfig
from ..conftest import available_textidstore_configs, redis_kvdriver_config, mongo_kvdriver_config, \
    inmemory_kvdriver_config, mixed_kvdriver_config, textidstore_instance
