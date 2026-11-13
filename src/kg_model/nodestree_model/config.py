from typing import Dict

from .agent_tasks.nodes_summarization import AgentSummNTaskConfigSelector
from ...db_drivers.tree_driver import TreeDriverConfig, TreeDBConnectionConfig
from ...db_drivers.tree_driver.utils import TreeNodeType
from ...db_drivers.vector_driver import VectorDriverConfig, VectorDBConnectionConfig
from ...rerankers import RerankerDriverConfig
from ...rerankers.methods import EnsembleFusionRerankerConfig
from ...utils import BaseAgentTaskConfigSelector

NODESTREE_MODEL_LOG_PATH = 'log/kg_model/nodes_tree'

NODESTREEM_AGENTASKS_SELECTORS_MAPPING: Dict[str, BaseAgentTaskConfigSelector] = {
    'nodes_summarization': AgentSummNTaskConfigSelector,
}

TREE_DB_DEFAULT_DRIVER_CONFIG = TreeDriverConfig(
    db_vendor='kuzu',
    db_config=TreeDBConnectionConfig(
        db_info={'db': 'DefaultDB', 'table': 'KuzuTree', 'expected_db_base_path': './personalai_tmp'},
        params={'buffer_pool_size': 1024**3,
                'table_type_map': {
                    'nodes': {
                        'forward': {TreeNodeType.root.value: 'root', TreeNodeType.leaf.value: 'leaf', TreeNodeType.summarized.value: 'summarized'}
                    }}
                },
        need_to_clear=False
    )
)

#

LEAFNODES_VDB_DEFAULT_DRIVER_CONFIGS_MAPPING = {
    'leaf_dense_nodes': VectorDriverConfig(
        db_vendor='chroma', db_config=VectorDBConnectionConfig(
            params={"hnsw:space": "ip", "hnsw:M": 4096},
            db_info={'db': 'default_db', 'table': "vectorized_leafnodes", 'expected_db_base_path': './personalai_tmp'},
            need_to_clear=False
        )
    ),
    'leaf_bm25_nodes': VectorDriverConfig(
        db_vendor='inmemory', vector_category='sparse_bm25', db_config=VectorDBConnectionConfig(
            db_info={'db': 'default_db', 'table': "sparsebm25_lnodes", 'expected_db_base_path': './personalai_tmp'},
            params={'save_on_disk': True, 'rewrite': True},
            need_to_clear=False
        )
    )
}

LNT_RERANKDRIVER_DEFAULT_CONFIG = RerankerDriverConfig(
    name='ensemble_fusion',
    strategy_config=EnsembleFusionRerankerConfig(
        vdb_names=['leaf_dense_nodes', 'leaf_bm25_nodes'],
        weights=[0.6, 0.4]
    )
)

#

SUMMNODES_VDB_DEFAULT_DRIVER_CONFIGS_MAPPING = {
    'summ_dense_nodes': VectorDriverConfig(
        db_vendor='chroma', db_config=VectorDBConnectionConfig(
            params={"hnsw:space": "ip", "hnsw:M": 4096},
            db_info={'db': 'default_db', 'table': "vectorized_summarizednodes", 'expected_db_base_path': './personalai_tmp'},
            need_to_clear=False
        )
    ),
    'summ_bm25_nodes': VectorDriverConfig(
        db_vendor='inmemory', vector_category='sparse_bm25', db_config=VectorDBConnectionConfig(
            db_info={'db': 'default_db', 'table': "sparsebm25_snodes", 'expected_db_base_path': './personalai_tmp'},
            params={'load_from_disk': True, 'save_on_disk': True, 'rewrite': True},
            need_to_clear=False
        )
    )
}

SNT_RERANKDRIVER_DEFAULT_CONFIG = RerankerDriverConfig(
    name='ensemble_fusion',
    strategy_config=EnsembleFusionRerankerConfig(
        vdb_names=['summ_dense_nodes', 'summ_bm25_nodes'],
        weights=[0.6, 0.4]
    )
)
