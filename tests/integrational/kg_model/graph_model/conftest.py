import pytest
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from typing import Dict

from src.kg_model.graph_model import GraphModel
from src.utils.data_structs import NodeType, RelationType
from src.db_drivers.graph_driver import GraphDriverConfig, GraphDBConnectionConfig
from src.kg_model import GraphModelConfig

from .available_graphmodel_configs import *
from .cases import AVAILABLE_GRAPH_MODELS

@pytest.fixture(scope='package')
def available_graphmodels(available_graphmodel_configs):
    graphmodel_connections_map: Dict[str, GraphModel] = dict()
    for graphdb_vendor in AVAILABLE_GRAPH_MODELS:
        config = available_graphmodel_configs[graphdb_vendor]
        graphmodel_connections_map[graphdb_vendor] = GraphModel(config)
        graphmodel_connections_map[graphdb_vendor].open_connections()

    return graphmodel_connections_map

@pytest.fixture(scope='function')
def graph_model(available_graphmodels, request):
    return available_graphmodels[request.param]
