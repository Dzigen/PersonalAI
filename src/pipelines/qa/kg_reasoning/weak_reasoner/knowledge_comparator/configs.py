from ......rerankers import RerankerDriverConfig
from ......rerankers.methods import EnsembleFusionRerankerConfig, RetrieverConfig

KC_MAIN_LOG_PATH = 'log/qa/kg_reasoner/weak/knowledge_comparator'

KC_RERANKDRIVER_DEFAULT_CONFIG = RerankerDriverConfig(
    name='ensemble_fusion',
    strategy_config=EnsembleFusionRerankerConfig(
        vdb_names=['dense_nodes', 'bm25_nodes'],
        weights=[0.3, 0.7]
    )
)
