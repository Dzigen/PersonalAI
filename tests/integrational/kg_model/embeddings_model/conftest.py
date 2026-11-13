import pytest
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from typing import Dict

from src.db_drivers.vector_driver.embedders import EmbedderModelConfig
from src.db_drivers.vector_driver import VectorDBConnectionConfig, VectorDriverConfig
from src.kg_model import EmbeddingsModelConfig
from src.db_drivers.vector_driver.embedders import EmbedderModelConfig, EmbedderModel
from src.kg_model.embeddings_model import EmbeddingsModel

from .available_embeddingsmodel_configs import *

from .cases import AVAILABLE_SPARSEBM25_DBS, AVAILABLE_DENSE_DBS

@pytest.fixture(scope='module')
def available_embeddingsmodels(available_embeddingsmodel_configs):
    embedder_config = EmbedderModelConfig(model_name_or_path=f'{PROJECT_BASE_DIR}models/intfloat/multilingual-e5-small', device='cuda')
    embedder = EmbedderModel(embedder_config)
    embedders_configs = {'dense_nodes': embedder, 'dense_triplets': embedder}

    embeddermodel_connections_map: Dict[str, EmbeddingsModel] = dict()
    for densedb_name in AVAILABLE_DENSE_DBS:
        for sparsedb_name in AVAILABLE_SPARSEBM25_DBS:
            kw_config = f"{densedb_name}/{sparsedb_name}"
            config = available_embeddingsmodel_configs[kw_config]
            
            embeddermodel_connections_map[kw_config] = EmbeddingsModel(embedders_configs, config)
            embeddermodel_connections_map[kw_config].open_connections()
            embeddermodel_connections_map[kw_config].check_consistency()

    return embeddermodel_connections_map


@pytest.fixture(scope='function')
def embeddings_model(available_embeddingsmodels, request):
    return available_embeddingsmodels[request.param]
