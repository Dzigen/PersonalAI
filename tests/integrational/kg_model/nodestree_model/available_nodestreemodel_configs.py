import pytest
import sys
from typing import Dict, Union
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.kg_model.nodestree_model import NodesTreeModelConfig
from src.rerankers import RerankerDriverConfig
from src.rerankers.methods import SingleStepRerankerConfig

from ...db_drivers.vector_driver.dense.available_dense_vector_configs import *
from ...db_drivers.tree_driver.available_tree_configs import *

@pytest.fixture(scope='session')
def available_nodestreemodel_configs(
    available_dense_vector_configs, available_tree_configs
):
    configs: Dict[str, Union[NodesTreeModelConfig, None]] = dict()
    for vectordb_vendor, vectordb_config in available_dense_vector_configs.items():
        for treedb_vendor, treedb_config in available_tree_configs.items():
            kw_config = f"{vectordb_vendor}/{treedb_vendor}"
            config = NodesTreeModelConfig(
                leafnodes_vdb_driver_configs_mapping={
                    'leaf_dense_nodes': vectordb_config
                },
                summnodes_vdb_driver_configs_mapping={
                    'summ_dense_nodes': vectordb_config
                },
                treedb_config=treedb_config,
                leafnodes_reranker_driver_config=RerankerDriverConfig(
                    name='single_step',
                    strategy_config=SingleStepRerankerConfig(vdb_name='leaf_dense_nodes')
                ),
                summnodes_reranker_driver_config=RerankerDriverConfig(
                    name='single_step',
                    strategy_config=SingleStepRerankerConfig(vdb_name='summ_dense_nodes')
                )
            )
            configs[kw_config] = deepcopy(config)
            configs[kw_config].leafnodes_vdb_driver_configs_mapping['leaf_dense_nodes'].db_config.db_info['name'] = 'leaf_nodes'
            configs[kw_config].summnodes_vdb_driver_configs_mapping['summ_dense_nodes'].db_config.db_info['name'] = 'summ_nodes'

    configs['None'] = None # костыль
    return configs
