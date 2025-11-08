import pytest
import sys
from typing import Dict
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.utils.data_structs import NodeType, RelationType
from src.db_drivers.graph_driver import GraphDriverConfig, GraphDBConnectionConfig
from src.db_drivers.vector_driver.embedders import EmbedderModelConfig, EmbedderModel
from src.db_drivers.vector_driver import VectorDBConnectionConfig, VectorDriverConfig
from src.db_drivers.tree_driver import TreeDriverConfig, TreeDBConnectionConfig
from src.db_drivers.tree_driver.utils import TreeNodeType
from src.kg_model import EmbeddingsModel, EmbeddingsModelConfig, GraphModel, GraphModelConfig, KnowledgeGraphModel, KnowledgeGraphModelConfig
from src.kg_model.nodestree_model import NodesTreeModelConfig
from src.agents import AgentDriver, AgentDriverConfig
from src.agents.utils import AgentConnectorConfig
from src.rerankers import RerankerDriverConfig
from src.rerankers.methods import SingleStepRerankerConfig
from src.kg_model.utils import KGEmbeddersMapping, AgentsMapping

#!!!AVAILABLE GRAPH MODELS!!!#

@pytest.fixture(scope='package')
def graph_neo4j_config():
    config = GraphModelConfig(
        driver_config=GraphDriverConfig(
            db_vendor='neo4j',
            db_config=GraphDBConnectionConfig(
                host="localhost", port="7680", db_info={'db': 'Testing', 'table': 'Graph'},
                params={'user': "neo4j", 'pwd': 'password'}, need_to_clear=True)))
    return config


@pytest.fixture(scope='package')
def graph_inmemory_config():
    config = GraphModelConfig(
        driver_config=GraphDriverConfig(
            db_vendor='inmemory_graph',
            db_config=GraphDBConnectionConfig(
                db_info={'db': 'testing', 'table': 'testing'},
                params={
                    'load_from_disk': False, 'load_dump_name': None, 'save_on_disk': True,
                    'load_dump_dir': f"{TEST_VOLUME_DIR}/inmemory_graph",
                    'save_dump_dir': f"{TEST_VOLUME_DIR}/inmemory_graph"},
                need_to_clear=True
            )
        )
    )
    return config


@pytest.fixture(scope='package')
def graph_kuzu_config():
    config = GraphModelConfig(
        driver_config=GraphDriverConfig(
            db_vendor='kuzu',
            db_config=GraphDBConnectionConfig(
                db_info={'db': 'Testing', 'table': 'Graph'},
                params={'path': f'{TEST_VOLUME_DIR}/kuzu', 'buffer_pool_size': 1024**3,
                        'table_type_map': {
                            'relations': {'forward': {RelationType.simple.value: 'simple', RelationType.hyper.value: 'hyper_rel', RelationType.episodic.value: 'episodic_rel'}, },
                            'nodes': {'forward': {NodeType.object.value: 'object', NodeType.hyper.value: 'hyper', NodeType.episodic.value: 'episodic'}}
                        }
                        },
                need_to_clear=True
            )
        )
    )
    return config


# ------------------------------#

@pytest.fixture(scope='package')
def available_graph_configs(
    graph_neo4j_config,
    graph_inmemory_config,
    graph_kuzu_config
):
    return {
        'neo4j': graph_neo4j_config,
        'inmemory_graph': graph_inmemory_config,
        'kuzu': graph_kuzu_config
    }


#!!!AVAILABLE VECTOR MODELS!!!#

@pytest.fixture(scope='package')
def embeddings_chroma_config():
    config = EmbeddingsModelConfig(
        nodesdb_driver_configs_mapping={
            'nodes_dense': VectorDriverConfig(
                db_vendor='chroma', db_config=VectorDBConnectionConfig(
                    conn={'path': f'{TEST_VOLUME_DIR}/chroma'},
                    db_info={'db': 'testing', 'table': 'vectorized_nodes'},
                      params={"hnsw:space": "ip", "hnsw:M": 4096}, need_to_clear=True
                )
            )
        },
        tripletsdb_driver_configs_mapping={
            'triplets_dense': VectorDriverConfig(
                db_vendor='chroma', db_config=VectorDBConnectionConfig(
                    conn={'path': f'{TEST_VOLUME_DIR}/chroma'},
                    db_info={'db': 'testing', 'table': 'vectorized_triplets'},
                    params={"hnsw:space": "ip", "hnsw:M": 4096}, need_to_clear=True
                )
            )
        }
    )
    return config


@pytest.fixture(scope='package')
def embeddings_milvus_config():

    config = EmbeddingsModelConfig(
        nodesdb_driver_configs_mapping={
            'nodes_dense': VectorDriverConfig(
                db_vendor='milvus', db_config=VectorDBConnectionConfig(
                    conn={'host': 'localhost', 'port': 19520, 'user': 'root', 'pass': 'Milvus'},
                    db_info={'db': 'testing', 'table': 'vectorized_nodes'}, need_to_clear=True,
                    params={'id_length': 32, 'vector_dim': 384, 'document_max_length': 51200, 'load': True, 'flush': True, 'create_sleep': 1, 'search_metric': 'IP'}
                )
            )
        },
        tripletsdb_driver_configs_mapping={
            'triplets_dense': VectorDriverConfig(
                db_vendor='milvus', db_config=VectorDBConnectionConfig(
                    conn={'host': 'localhost', 'port': 19520, 'user': 'root', 'pass': 'Milvus'},
                    db_info={'db': 'testing', 'table': 'vectorized_triplets'}, need_to_clear=True,
                    params={'id_length': 32, 'vector_dim': 384, 'document_max_length': 51200, 'load': True, 'flush': True, 'create_sleep': 1, 'search_metric': 'IP'}
                )
            )
        }
    )

    return config

@pytest.fixture(scope='package')
def embeddings_inmemory_config():
    config = EmbeddingsModelConfig(
        nodesdb_driver_configs_mapping={
            'nodes_dense': VectorDriverConfig(
                db_vendor='inmemory',
                db_config=VectorDBConnectionConfig(
                    db_info={'db': 'testing', 'table': 'vectorized_nodes'},
                    params={
                        'store_dump_name': 'inmemory_dense',
                        'load_from_disk': False,
                        'load_dump_dir': f"{TEST_VOLUME_DIR}/inmemory_dense",
                        'save_on_disk': False,
                        'save_dump_dir': f"{TEST_VOLUME_DIR}/inmemory_dense",
                        'vector_dim': 384
                    }
                )
            )
        },
        tripletsdb_driver_configs_mapping={
            'triplets_dense': VectorDriverConfig(
                db_vendor='inmemory',
                db_config=VectorDBConnectionConfig(
                    db_info={'db': 'testing', 'table': 'vectorized_triplets'},
                    params={
                        'store_dump_name': 'inmemory_dense',
                        'load_from_disk': False,
                        'load_dump_dir': f"{TEST_VOLUME_DIR}/inmemory_dense",
                        'save_on_disk': False,
                        'save_dump_dir': f"{TEST_VOLUME_DIR}/inmemory_dense",
                        'vector_dim': 384
                    }
                )
            )
        }
    )
    return config

@pytest.fixture(scope='package')
def embeddings_elasticsearch_config():
    config = EmbeddingsModelConfig(
        nodesdb_driver_configs_mapping={
            'nodes_dense': VectorDriverConfig(
                db_vendor='elasticsearch',
                db_config=VectorDBConnectionConfig(
                    db_info={'db': 'testing', 'table': 'vectorized_nodes'},
                    conn={'host': 'localhost', 'port': 9201}
                )
            )
        },
        tripletsdb_driver_configs_mapping={
            'triplets_dense': VectorDriverConfig(
                db_vendor='elasticsearch',
                db_config=VectorDBConnectionConfig(
                    db_info={'db': 'testing', 'table': 'vectorized_triplets'},
                    conn={'host': 'localhost', 'port': 9201}
                )
            )
        }
    )
    return config

# ------------------------------#

@pytest.fixture(scope='package')
def available_embedding_configs(
    embeddings_chroma_config, embeddings_milvus_config, embeddings_inmemory_config, embeddings_elasticsearch_config
):
    return {
        'chroma': embeddings_chroma_config,
        'milvus': embeddings_milvus_config,
        'inmemory': embeddings_inmemory_config,
        'elasticsearch': embeddings_elasticsearch_config
    }


#!!!AVAILABLE NODESTREE MODELS!!!#

@pytest.fixture(scope='package')
def nodestree_milvus_kuzu_config():
    return NodesTreeModelConfig(
        leafnodes_vdb_driver_configs_mapping={
            'leaf_dense_nodes': VectorDriverConfig(
                db_vendor='milvus', db_config=VectorDBConnectionConfig(
                    conn={'host': 'localhost', 'port': 19520, 'user': 'root', 'pass': 'Milvus'},
                    db_info={'db': 'testing', 'table': 'leaf_object_nodes'}, need_to_clear=True,
                    params={'id_length': 32, 'vector_dim': 384, 'document_max_length': 51200, 'load': True, 'flush': True, 'create_sleep': 1, 'search_metric': 'IP'}
                )
            )
        },
        summnodes_vdb_driver_configs_mapping={
            'summ_dense_nodes': VectorDriverConfig(
                db_vendor='milvus', db_config=VectorDBConnectionConfig(
                    conn={'host': 'localhost', 'port': 19520, 'user': 'root', 'pass': 'Milvus'},
                    db_info={'db': 'testing', 'table': 'summ_nodes'}, need_to_clear=True,
                    params={'id_length': 32, 'vector_dim': 384, 'document_max_length': 51200, 'load': True, 'flush': True, 'create_sleep': 1, 'search_metric': 'IP'}
                )
            )
        },
        treedb_config=TreeDriverConfig(
            db_vendor='kuzu',
            db_config=TreeDBConnectionConfig(
                db_info={'db': 'Testing', 'table': 'NodesTree'},
                params={'path': f"{TEST_VOLUME_DIR}/kuzu_tree", 'buffer_pool_size': 1024**3,
                        'table_type_map': {
                            'nodes': {'forward': {TreeNodeType.root.value: 'root', TreeNodeType.leaf.value: 'leaf', TreeNodeType.summarized.value: 'summarized'}}
                        }
                },
                need_to_clear=True
            )
        ),
        leafnodes_reranker_driver_config=RerankerDriverConfig(
            name='single_step',
            strategy_config=SingleStepRerankerConfig(vdb_name='leaf_dense_nodes')
        ),
        summnodes_reranker_driver_config=RerankerDriverConfig(
            name='single_step',
            strategy_config=SingleStepRerankerConfig(vdb_name='summ_dense_nodes')
        ),
    )


@pytest.fixture(scope='package')
def nodestree_milvus_neo4j_config():
    return NodesTreeModelConfig(
        leafnodes_vdb_driver_configs_mapping={
            'leaf_dense_nodes': VectorDriverConfig(
                db_vendor='milvus', db_config=VectorDBConnectionConfig(
                    conn={'host': 'localhost', 'port': 19520, 'user': 'root', 'pass': 'Milvus'},
                    db_info={'db': 'testing', 'table': 'leaf_nodes'}, need_to_clear=True,
                    params={'id_length': 32, 'vector_dim': 384, 'document_max_length': 51200, 'load': True, 'flush': True, 'create_sleep': 1, 'search_metric': 'IP'}
                )
            )
        },
        summnodes_vdb_driver_configs_mapping={
            'summ_dense_nodes': VectorDriverConfig(
                db_vendor='milvus', db_config=VectorDBConnectionConfig(
                    conn={'host': 'localhost', 'port': 19520, 'user': 'root', 'pass': 'Milvus'},
                    db_info={'db': 'testing', 'table': 'summ_nodes'}, need_to_clear=True,
                    params={'id_length': 32, 'vector_dim': 384, 'document_max_length': 51200, 'load': True, 'flush': True, 'create_sleep': 1, 'search_metric': 'IP'}
                )
            )
        },
        treedb_config=TreeDriverConfig(
            db_vendor='neo4j',
            db_config=TreeDBConnectionConfig(
                host="localhost", port="7680",
                db_info={'db': 'Testing', 'table': 'NodesTree'},
                params={'user': "neo4j", 'pwd': 'password'},
                need_to_clear=True
            )
        ),
        leafnodes_reranker_driver_config=RerankerDriverConfig(
            name='single_step',
            strategy_config=SingleStepRerankerConfig(vdb_name='leaf_dense_nodes')
        ),
        summnodes_reranker_driver_config=RerankerDriverConfig(
            name='single_step',
            strategy_config=SingleStepRerankerConfig(vdb_name='summ_dense_nodes')
        ),
    )


@pytest.fixture(scope='package')
def nodestree_chroma_kuzu_config():
    return NodesTreeModelConfig(
        leafnodes_vdb_driver_configs_mapping={
            'leaf_dense_nodes': VectorDriverConfig(
                db_vendor='chroma', db_config=VectorDBConnectionConfig(
                    conn={'path': f'{TEST_VOLUME_DIR}/chroma'},
                    db_info={'db': 'testing', 'table': 'leaf_nodes'},
                      params={"hnsw:space": "ip", "hnsw:M": 4096}, need_to_clear=True
                )
            )
        },
        summnodes_vdb_driver_configs_mapping={
            'summ_dense_nodes': VectorDriverConfig(
                db_vendor='chroma', db_config=VectorDBConnectionConfig(
                    conn={'path': f'{TEST_VOLUME_DIR}/chroma'},
                    db_info={'db': 'testing', 'table': 'summ_nodes'},
                      params={"hnsw:space": "ip", "hnsw:M": 4096}, need_to_clear=True
                )
            )
        },
        treedb_config=TreeDriverConfig(
            db_vendor='kuzu',
            db_config=TreeDBConnectionConfig(
                db_info={'db': 'Testing', 'table': 'NodesTree'},
                params={'path': f"{TEST_VOLUME_DIR}/kuzu_tree", 'buffer_pool_size': 1024**3,
                        'table_type_map': {
                            'nodes': {'forward': {TreeNodeType.root.value: 'root', TreeNodeType.leaf.value: 'leaf', TreeNodeType.summarized.value: 'summarized'}}
                        }
                },
                need_to_clear=True
            )
        ),
        leafnodes_reranker_driver_config=RerankerDriverConfig(
            name='single_step',
            strategy_config=SingleStepRerankerConfig(vdb_name='leaf_dense_nodes')
        ),
        summnodes_reranker_driver_config=RerankerDriverConfig(
            name='single_step',
            strategy_config=SingleStepRerankerConfig(vdb_name='summ_dense_nodes')
        )
    )

@pytest.fixture(scope='package')
def nodestree_chroma_neo4j_config():
    return NodesTreeModelConfig(
        leafnodes_vdb_driver_configs_mapping={
            'leaf_dense_nodes': VectorDriverConfig(
                db_vendor='chroma', db_config=VectorDBConnectionConfig(
                    conn={'path': f'{TEST_VOLUME_DIR}/chroma'},
                    db_info={'db': 'testing', 'table': 'leaf_nodes'},
                      params={"hnsw:space": "ip", "hnsw:M": 4096}, need_to_clear=True
                )
            )
        },
        summnodes_vdb_driver_configs_mapping={
            'summ_dense_nodes': VectorDriverConfig(
                db_vendor='chroma', db_config=VectorDBConnectionConfig(
                    conn={'path': f'{TEST_VOLUME_DIR}/chroma'},
                    db_info={'db': 'testing', 'table': 'summ_nodes'},
                      params={"hnsw:space": "ip", "hnsw:M": 4096}, need_to_clear=True
                )
            )
        },
        treedb_config=TreeDriverConfig(
            db_vendor='neo4j',
            db_config=TreeDBConnectionConfig(
                host="localhost", port="7680",
                db_info={'db': 'Testing', 'table': 'NodesTree'},
                params={'user': "neo4j", 'pwd': 'password'},
                need_to_clear=True
            )
        ),
        leafnodes_reranker_driver_config=RerankerDriverConfig(
            name='single_step',
            strategy_config=SingleStepRerankerConfig(vdb_name='leaf_dense_nodes')
        ),
        summnodes_reranker_driver_config=RerankerDriverConfig(
            name='single_step',
            strategy_config=SingleStepRerankerConfig(vdb_name='summ_dense_nodes')
        )
    )


# ------------------------------#

@pytest.fixture(scope='package')
def available_nodestree_configs(
    nodestree_milvus_kuzu_config, nodestree_milvus_neo4j_config,
    nodestree_chroma_kuzu_config, nodestree_chroma_neo4j_config
):
    return {
        'milvus_kuzu': nodestree_milvus_kuzu_config,
        'milvus_neo4j': nodestree_milvus_neo4j_config,
        'chroma_kuzu': nodestree_chroma_kuzu_config,
        'chroma_neo4j': nodestree_chroma_neo4j_config,
        'None': None
    }

# ------------------------------#


@pytest.fixture(scope='package')
def available_kg_configs(
    available_embedding_configs: Dict[str, EmbeddingsModelConfig],
    available_graph_configs: Dict[str, GraphModelConfig],
    available_nodestree_configs: Dict[str, NodesTreeModelConfig]):

    e5small_config = EmbedderModelConfig(model_name_or_path=f'{PROJECT_BASE_DIR}models/intfloat/multilingual-e5-small', device='cuda')
    embedders_map = KGEmbeddersMapping(
        embeddings_model={'nodes_dense': 'm-e5-small', 'triplets_dense': 'm-e5-small'},
        nodestree_model={'leaf_dense_nodes': 'm-e5-small', 'summ_dense_nodes': 'm-e5-small'}
    )
    embedders_configs = {'m-e5-small': e5small_config}

    llamaagent_config = AgentDriverConfig(
        name='ollama',
        agent_config=AgentConnectorConfig(
            gen_strategy={"num_predict": 2048, "seed": 42, "top_k": 1, "temperature": 0.0},
            credentials={"model": 'llama3.1:8b', "host": 'localhost', "port": 11437},
            ext_params={"timeout": 560, "keep_alive": -1}))
    agents_configs = {'llama3.1:8b': llamaagent_config}
    agents_map = AgentsMapping(
        mem_pipeline='llama3.1:8b',
        qa_pipeline='llama3.1:8b',
        kg_nodestree_model='llama3.1:8b'
    )

    kg_configs = {}
    for vector_name, vector_config in available_embedding_configs.items():
        for graph_name, graph_config in available_graph_configs.items():
            for nodestree_name, nodestree_config in available_nodestree_configs.items():
                cur_config = KnowledgeGraphModelConfig(
                    graph_struct_config=graph_config,
                    graph_embeddings_config=vector_config,
                    nodestree_config=nodestree_config,
                    embedders_configs=embedders_configs,embedders_map=embedders_map,
                    agents_configs=agents_configs,agents_map=agents_map)
                kg_configs[f"{vector_name}/{graph_name}/{nodestree_name}"] = cur_config
    return kg_configs

@pytest.fixture(scope='function')
def kg_model(available_kg_configs, request):
    kg_model = KnowledgeGraphModel(available_kg_configs[request.param])

    return kg_model
