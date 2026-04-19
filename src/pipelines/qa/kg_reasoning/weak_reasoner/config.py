from ..weak_reasoner.knowledge_retriever import KnowledgeRetrieverConfig
from ..weak_reasoner.knowledge_retriever.traversal_methods import MixturedGraphSearchConfig, GraphBeamSearchConfig
from .....utils.data_structs import NodeType

WKGR_MAIN_LOG_PATH = 'log/qa/kg_reasoner/weak/main'


WEAK_KG_RETRIEVER_CONFIG = KnowledgeRetrieverConfig(
    retriever_method='mixture',
    retriever_config=MixturedGraphSearchConfig(
        retriever1_name='beamsearch',
        retriever1_config=GraphBeamSearchConfig(
            max_depth=5,
            max_paths=10,
        ),
        accepted_node_types=[NodeType.object, NodeType.hyper, NodeType.episodic, NodeType.time]
    )
)
