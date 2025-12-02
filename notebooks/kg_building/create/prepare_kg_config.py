print("Creating KnowledgeGraph config file...")
import sys
import joblib
import yaml

####################################################
print("1. Loading hyperparameters from .yaml files")

# Read YAML file (kg-conn)
KGCONN_FILE_PATH = sys.orig_argv[2]
with open(KGCONN_FILE_PATH, 'r') as stream:
    KGCONN_PARAMS = yaml.safe_load(stream)

# Read YAML file (kg-env)
KGENV_FILE_PATH = sys.orig_argv[3]
with open(KGENV_FILE_PATH, 'r') as stream:
    KGENV_PARAMS = yaml.safe_load(stream)

# Read YAML file (kg-hyperp)
KGHYPERP_FILE_PATH = sys.orig_argv[4]
with open(KGHYPERP_FILE_PATH, 'r') as stream:
    KGHYPERP_PARAMS = yaml.safe_load(stream)


sys.path.insert(0, KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path'])

from src.db_drivers.vector_driver import VectorDBConnectionConfig, VectorDBConnectionConfig, VectorDriverConfig, EmbedderModelConfig
from src.db_drivers.graph_driver import GraphDriverConfig, GraphDBConnectionConfig, GraphDBConnectionConfig
from src.kg_model import EmbeddingsModelConfig, GraphModelConfig, KnowledgeGraphModelConfig
from src.agents import AgentDriverConfig
from src.kg_model.utils import AgentsMapping, KGEmbeddersMapping
from src.agents.utils import AgentConnectorConfig

####################################################
print("2. Setting paths")

DATASET_KGS_PATH = f"{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['base_path']}/{KGENV_PARAMS['WORKSPACE_CONTAINER_DIRS']['kg']}/{KGHYPERP_PARAMS['DATASET_NAME']}"
SPEC_KG_PATH = f"{DATASET_KGS_PATH}/{KGHYPERP_PARAMS['KNOWLEDGE_GRAPH_NAME']}"

KG_MODEL_CONFIG_PATH = f"{SPEC_KG_PATH}/{KGENV_PARAMS['SAVE_CONFIGS_NAMES']['kg_config']}"

####################################################
print("3. Setting Graph Config")

GRAPHDB_CONFIG = KGCONN_PARAMS['KG_MODEL_CONNECTORS']['graph_struc_connection']

graphdb_config = GraphDBConnectionConfig(
    host=GRAPHDB_CONFIG['host'],
    port=GRAPHDB_CONFIG['port'],
    db_info=GRAPHDB_CONFIG['db_info'],
    params=GRAPHDB_CONFIG['params']
)

gmodel_config = GraphModelConfig(
    driver_config=GraphDriverConfig(
        db_vendor='neo4j', # !!! PAY ATTENTION !!!
        db_config=graphdb_config))

####################################################
print("4. Setting Embeddings Config")

########## nodes dbs ##########

DENSE_NODESDB_CONFIG = KGCONN_PARAMS['KG_MODEL_CONNECTORS']['embeddings_struc_connection']['nodesdb_config']['dense_connector']
dense_nodesdb_config = VectorDBConnectionConfig(
    db_info=DENSE_NODESDB_CONFIG['db_info'],
    params=DENSE_NODESDB_CONFIG['params'],
    conn=DENSE_NODESDB_CONFIG['conn']
)
dense_ndbdriver_config = VectorDriverConfig(
    db_vendor='milvus', # !!! PAY ATTENTION !!!
    vector_category='dense',
    db_config=dense_nodesdb_config
)

SPARSE_NODESDB_CONFIG = KGCONN_PARAMS['KG_MODEL_CONNECTORS']['embeddings_struc_connection']['nodesdb_config']['sparse_connector']
sparse_nodesdb_config = VectorDBConnectionConfig(
    db_info=SPARSE_NODESDB_CONFIG['db_info'],
    conn=SPARSE_NODESDB_CONFIG['conn']
)
sparse_ndbdriver_config = VectorDriverConfig(
    db_vendor='opensearch', # !!! PAY ATTENTION !!!
    vector_category='sparse_bm25',
    db_config=sparse_nodesdb_config
)

########## triplets dbs ##########

DENSE_TRIPLETSDB_CONFIG = KGCONN_PARAMS['KG_MODEL_CONNECTORS']['embeddings_struc_connection']['tripletsdb_config']['dense_connector']
dense_tripletsdb_config = VectorDBConnectionConfig(
    db_info=DENSE_TRIPLETSDB_CONFIG['db_info'],
    params=DENSE_TRIPLETSDB_CONFIG['params'],
    conn=DENSE_TRIPLETSDB_CONFIG['conn']
)
dense_tdbdriver_config = VectorDriverConfig(
    db_vendor='milvus', # !!! PAY ATTENTION !!!
    vector_category='dense',
    db_config=dense_tripletsdb_config
)

SPARSE_TRIPLETSDB_CONFIG = KGCONN_PARAMS['KG_MODEL_CONNECTORS']['embeddings_struc_connection']['tripletsdb_config']['sparse_connector']
sparse_tripletsdb_config = VectorDBConnectionConfig(
    db_info=SPARSE_TRIPLETSDB_CONFIG['db_info'],
    conn=SPARSE_TRIPLETSDB_CONFIG['conn']
)
sparse_tdbdriver_config = VectorDriverConfig(
    db_vendor='opensearch', # !!! PAY ATTENTION !!!
    vector_category='sparse_bm25',
    db_config=sparse_tripletsdb_config
)

emodel_config = EmbeddingsModelConfig(
    nodesdb_driver_configs_mapping={
        DENSE_NODESDB_CONFIG['name']: dense_ndbdriver_config,
        SPARSE_NODESDB_CONFIG['name']: sparse_ndbdriver_config
    },
    tripletsdb_driver_configs_mapping={
        DENSE_TRIPLETSDB_CONFIG['name']: dense_tdbdriver_config,
        SPARSE_TRIPLETSDB_CONFIG['name']: sparse_tdbdriver_config
    }
)

############## Mappers ##################

DEFAULT_EMBEDDER_CONFIG = KGHYPERP_PARAMS['KG_CONFIG']['embedder_configs']['default']
embedders_configs = {
    'default': EmbedderModelConfig(
        model_name_or_path=DEFAULT_EMBEDDER_CONFIG['model_name_or_path'],
        prompts=DEFAULT_EMBEDDER_CONFIG ['prompts']
    )
}
embedders_map = KGEmbeddersMapping(**KGHYPERP_PARAMS['KG_CONFIG']['embedders_mapping'])

DEFAULT_AGENT_CONFIG = KGHYPERP_PARAMS['KG_CONFIG']['agent_configs']['default']
agents_configs = {
    'default': AgentDriverConfig(
        name=DEFAULT_AGENT_CONFIG['vendor'],
        agent_config=AgentConnectorConfig(
            gen_strategy=DEFAULT_AGENT_CONFIG['gen_strategy'],
            credentials=DEFAULT_AGENT_CONFIG['credentials'],
            ext_params=DEFAULT_AGENT_CONFIG['ext_params']
        )
    )
}
agents_map = AgentsMapping(**KGHYPERP_PARAMS['KG_CONFIG']['agents_mapping'])

####################################################
print("5. Setting KG Config")

kgmodel_config = KnowledgeGraphModelConfig(
    graph_struct_config=gmodel_config,
    graph_embeddings_config=emodel_config,
    embedders_configs=embedders_configs,
    embedders_map=embedders_map,
    agents_configs=agents_configs,
    agents_map=agents_map
)

####################################################
print("6. Saving KG Config")

print("kg_model: ", kgmodel_config)
joblib.dump(kgmodel_config, KG_MODEL_CONFIG_PATH)

print("############ DONE ############")
