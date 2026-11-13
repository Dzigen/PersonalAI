import pytest
from typing import Dict
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.db_drivers.vector_driver.embedders import EmbedderModelConfig
from src.kg_model.embeddings_model import EmbeddingsModelConfig
from src.kg_model.graph_model import GraphModelConfig
from src.kg_model.nodestree_model import NodesTreeModelConfig
from src.kg_model import KnowledgeGraphModelConfig
from src.kg_model.utils import KGEmbeddersMapping, AgentsMapping
from src.agents import AgentDriverConfig
from src.agents.utils import AgentConnectorConfig

from .embeddings_model.available_embeddingsmodel_configs import *
from .graph_model.available_graphmodel_configs import *
from .nodestree_model.available_nodestreemodel_configs import *

@pytest.fixture(scope='session')
def available_kgmodel_configs(
    available_embeddingsmodel_configs: Dict[str, EmbeddingsModelConfig],
    available_graphmodel_configs: Dict[str, GraphModelConfig],
    available_nodestreemodel_configs: Dict[str, NodesTreeModelConfig]):

    e5small_config = EmbedderModelConfig(model_name_or_path=f'{PROJECT_BASE_DIR}models/intfloat/multilingual-e5-small', device='cuda')
    embedders_map = KGEmbeddersMapping(
        embeddings_model={'dense_nodes': 'm-e5-small', 'dense_triplets': 'm-e5-small'},
        nodestree_model=None
    )
    embedders_configs = {'m-e5-small': e5small_config}

    llamaagent_config = AgentDriverConfig(
        name='ollama',
        agent_config=AgentConnectorConfig(
            gen_strategy={"num_predict": 2048, "seed": 42, "top_k": 1, "temperature": 0.0},
            credentials={"model": 'qwen2.5:7b', "host": 'localhost', "port": 11437},
            ext_params={"timeout": 560, "keep_alive": -1}
        )
    )
    agents_configs = {'qwen2.5:7b': llamaagent_config}
    agents_map = AgentsMapping(
        mem_pipeline='qwen2.5:7b',
        qa_pipeline='qwen2.5:7b',
        kg_nodestree_model='qwen2.5:7b'
    )

    configs: Dict[str, KnowledgeGraphModelConfig] = dict()
    for em_name, em_config  in available_embeddingsmodel_configs.items():
        for gm_name, gm_config in available_graphmodel_configs.items():
            for ntm_name, ntm_config in available_nodestreemodel_configs.items():
                config = KnowledgeGraphModelConfig(
                    graph_struct_config=gm_config,
                    graph_embeddings_config=em_config,
                    nodestree_config=ntm_config,
                    embedders_configs=embedders_configs,
                    embedders_map=embedders_map, 
                    agents_configs=agents_configs,
                    agents_map=agents_map,
                    log_base_path=TEST_VOLUME_DIR
                )
                configs[f"{em_name}/{gm_name}/{ntm_name}"] = deepcopy(config)

    return configs