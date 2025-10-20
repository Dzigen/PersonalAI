from .......rerankers import RerankerDriverConfig
from .......rerankers.methods import EnsembleFusionRerankerConfig, RetrieverConfig

KRFILTER_RERANKDRIVER_DEFAULT_CONFIG = RerankerDriverConfig(
    name='ensemble_fusion',
    strategy_config=EnsembleFusionRerankerConfig(
        vdb_names=['triplets_dense', 'triplets_sparse_bm25'],
        retriever_configs=[RetrieverConfig(fetch_n=50, threshold=0.5), RetrieverConfig(fetch_n=50, threshold=0.5)],
        weights=[0.7, 0.3]
    )
)
