from ...db_drivers.tree_driver import TreeDriverConfig
from ...db_drivers.vector_driver import VectorDriverConfig, VectorDBConnectionConfig

DEFAULT_NSUMM_TASK_CONFIG = ...

NODESTREE_MODEL_LOG_PATH = 'log/kg_model/nodes_tree'

SUMMNODES_VDB_DEFAULT_DRIVER_CONFIG = VectorDriverConfig(
    db_vendor='chroma', db_config=VectorDBConnectionConfig(
        conn={'path':"../data/graph_structures/vectorized_triplets/default_densedb"},
        db_info={'db': 'default_db', 'table': "vectorized_summarizednodes"}))

BASE_VDB_DEFAULT_DRIVER_CONFIG = VectorDriverConfig(
    db_vendor='chroma', db_config=VectorDBConnectionConfig(
        conn={'path':"../data/graph_structures/vectorized_triplets/default_densedb"},
        db_info={'db': 'default_db', 'table': "vectorized_nodes"}))

TREE_DB_DEFAULT_DRIVER_CONFIG = TreeDriverConfig(db_vendor='neo4j', db_config=...)
