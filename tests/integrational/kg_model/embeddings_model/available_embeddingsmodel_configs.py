import pytest
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from typing import Dict
from copy import deepcopy

from src.db_drivers.vector_driver.embedders import EmbedderModelConfig
from src.db_drivers.vector_driver import VectorDBConnectionConfig, VectorDriverConfig
from src.kg_model import EmbeddingsModelConfig
from src.db_drivers.vector_driver.embedders import EmbedderModelConfig, EmbedderModel
from src.kg_model.embeddings_model import EmbeddingsModel

from ...db_drivers.vector_driver.dense.available_dense_vector_configs import *
from ...db_drivers.vector_driver.sparse_bm25.available_sparse_vector_configs import *

@pytest.fixture(scope='session')
def available_embeddingsmodel_configs(available_dense_vector_configs, available_sparsebm25_vector_configs):

    configs: Dict[str, EmbeddingsModelConfig] = dict()
    for dense_vendor, dense_config in available_dense_vector_configs.items():
        for sparse_vendor, sparse_config in available_sparsebm25_vector_configs.items():
            config_kw = f"{dense_vendor}/{sparse_vendor}"
            config = EmbeddingsModelConfig(
                nodesdb_driver_configs_mapping={
                    'dense_nodes': deepcopy(dense_config),
                    'bm25_nodes': deepcopy(sparse_config)

                },
                tripletsdb_driver_configs_mapping={
                    'dense_triplets': deepcopy(dense_config),
                    'bm25_triplets': deepcopy(sparse_config)
                },
                log_base_path=TEST_VOLUME_DIR
            )

            config.nodesdb_driver_configs_mapping['dense_nodes'].db_config.db_info['table'] = "dense_nodes"
            config.nodesdb_driver_configs_mapping['bm25_nodes'].db_config.db_info['table'] = "sparsebm25_nodes"
            config.tripletsdb_driver_configs_mapping['dense_triplets'].db_config.db_info['table'] = "dense_triplets"
            config.tripletsdb_driver_configs_mapping['bm25_triplets'].db_config.db_info['table'] = "sparsebm25_triplets"

            config.nodesdb_driver_configs_mapping['dense_nodes'].db_config.params['vector_dim'] = 384 # !!! PAY ATTENTION !!!
            config.tripletsdb_driver_configs_mapping['dense_triplets'].db_config.params['vector_dim'] = 384 # !!! PAY ATTENTION !!!

            configs[config_kw] = deepcopy(config)

    return configs