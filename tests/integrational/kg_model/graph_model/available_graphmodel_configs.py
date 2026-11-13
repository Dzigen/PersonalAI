import pytest
import sys
from copy import deepcopy

# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from typing import Dict

from src.kg_model.graph_model import GraphModel
from src.utils.data_structs import NodeType, RelationType
from src.db_drivers.graph_driver import GraphDriverConfig, GraphDBConnectionConfig
from src.kg_model import GraphModelConfig

from ...db_drivers.graph_driver.available_graph_configs import *

@pytest.fixture(scope='session')
def available_graphmodel_configs(available_graph_configs):
    configs: Dict[str, GraphModelConfig] = dict()
    for vendor_name, dbdriver_config in available_graph_configs.items():
        configs[vendor_name] = GraphModelConfig(
            driver_config=deepcopy(dbdriver_config),
            log_base_path=TEST_VOLUME_DIR
        )
    return configs