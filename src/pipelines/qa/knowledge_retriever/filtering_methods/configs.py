from .....rerankers import RerankerDriverConfig
from .....rerankers.methods import EnsembleFusionRerankerConfig, RetrieverConfig

TFILTER_LOG_PATH = 'log/qa/knowledge_retriever/triples_filter'

KRFILTER_RERANKDRIVER_DEFAULT_CONFIG = RerankerDriverConfig(
    name='ensemble_fusion',
    strategy_config=EnsembleFusionRerankerConfig(
        vdb_names=['dense_triplets', 'bm25_triplets'],
        retriever_configs=[RetrieverConfig(fetch_n=50, threshold=0.5), RetrieverConfig(fetch_n=50, threshold=0.5)],
        weights=[0.9, 0.1]
    )
)
