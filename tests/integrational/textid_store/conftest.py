import pytest
import sys
from typing import Dict, List
from copy import deepcopy
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from .available_textidstore_configs import *

from src.TextIdStore import TextIdStore

@pytest.fixture(scope='function')
def textidstore_instance(available_textidstore_configs: Dict, request):
    config = available_textidstore_configs[request.param]
    idstore = TextIdStore(config)
    idstore.open_connections()
    return idstore
