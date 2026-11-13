import pytest
from typing import Dict
from copy import deepcopy
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.kg_model import KnowledgeGraphModel

from .available_kgmodel_configs import *
from .cases import AVAILABLE_GRAPH_DBS, AVAILABLE_DENSE_DBS, AVAILABLE_SPARSEBM25_DBS, AVAILABLE_NODESTREE_MODELS

# ------------------------------#

@pytest.fixture(scope='module')
def available_kg_models(available_kgmodel_configs):
    kg_configs: Dict[str, KnowledgeGraphModel] = dict()
    for graphdb_vendor in AVAILABLE_GRAPH_DBS:
        for densedb_vendor in AVAILABLE_DENSE_DBS:
            for sparsedb_vendor in AVAILABLE_SPARSEBM25_DBS:
                for nodestreedb_vendor in AVAILABLE_NODESTREE_MODELS:
                    kw_config = f"{densedb_vendor}/{sparsedb_vendor}/{graphdb_vendor}/{nodestreedb_vendor}"
                    config = deepcopy(available_kgmodel_configs[kw_config])
                    
                    kg_configs[kw_config] = KnowledgeGraphModel(config)
                    kg_configs[kw_config].open_connections()

    return kg_configs


@pytest.fixture(scope='function')
def kg_model(available_kg_models, request):
    return available_kg_models[request.param]
