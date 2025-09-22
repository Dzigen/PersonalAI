from ...db_drivers.tree_driver import TreeDriverConfig, TreeDBConnectionConfig
from ...db_drivers.tree_driver.utils import TreeNodeType
from ...db_drivers.vector_driver import VectorDriverConfig, VectorDBConnectionConfig
from .agent_tasks.nodes_summarization import AgentSummNTaskConfigSelector

DEFAULT_SUMMN_TASK_CONFIG = AgentSummNTaskConfigSelector.select(
    base_config_version='v1')

NODESTREE_MODEL_LOG_PATH = 'log/kg_model/nodes_tree'

SUMMNODES_VDB_DEFAULT_DRIVER_CONFIG = VectorDriverConfig(
    db_vendor='chroma', db_config=VectorDBConnectionConfig(
        conn={
            'path': "./personalai_tmp/graph_structures/tree_model/vectorized_nodes/chroma/default_densedb"},
        params={"hnsw:space": "ip", "hnsw:M": 4096},
        db_info={'db': 'default_db', 'table': "vectorized_summarizednodes"}))

LEAFNODES_VDB_DEFAULT_DRIVER_CONFIG = VectorDriverConfig(
    db_vendor='chroma', db_config=VectorDBConnectionConfig(
        conn={
            'path': "./personalai_tmp/graph_structures/tree_model/vectorized_nodes/chroma/default_densedb"},
        params={"hnsw:space": "ip", "hnsw:M": 4096},
        db_info={'db': 'default_db', 'table': "vectorized_leafnodes"}))

TREE_DB_DEFAULT_DRIVER_CONFIG = TreeDriverConfig(
    db_vendor='kuzu',
    db_config=TreeDBConnectionConfig(
        params={'path': './personalai_tmp//graph_structures/tree_model/tree_struct/kuzu', 'buffer_pool_size': 1024**3,
                'table_type_map': {
                    'nodes': {
                        'forward': {TreeNodeType.root.value: 'root', TreeNodeType.leaf.value: 'leaf', TreeNodeType.summarized.value: 'summarized'}
                    }}
                },
        need_to_clear=False
    )
)
