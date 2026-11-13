import pytest
from typing import Dict
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.utils.cache_kv import CacheKV
from ...db_drivers.kv_driver.available_kv_configs import *
from .cases import AVAILABLE_KV_DBS

@pytest.fixture(scope='package')
def available_cachekv_connections(available_kv_configs):
    cachekv_conns: Dict[str, CacheKV] = dict()
    for kvdb_vendor in AVAILABLE_KV_DBS:
        config = deepcopy(available_kv_configs[kvdb_vendor])
        config.db_config.db_info['expected_db_base_path'] = TEST_VOLUME_DIR
        config.db_config.need_to_clear = True
        cachekv_conns[kvdb_vendor] = CacheKV(config)
        cachekv_conns[kvdb_vendor].open_connections()
    return cachekv_conns 


@pytest.fixture(scope='function')
def cachekv_conn(available_cachekv_connections, request):
    return available_cachekv_connections[request.param]
