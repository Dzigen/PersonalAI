import pytest
import sys
from typing import Dict
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.kg_model import KnowledgeGraphModel

from ...integrational.kg_model.available_kgmodel_configs import *

@pytest.fixture(scope='function')
def kg_model(available_kgmodel_configs, request):
    kg_model = KnowledgeGraphModel(available_kgmodel_configs[request.param])
    kg_model.open_connections()

    return kg_model
