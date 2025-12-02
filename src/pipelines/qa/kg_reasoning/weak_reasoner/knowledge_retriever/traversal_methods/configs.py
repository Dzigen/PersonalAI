from .......rerankers import RerankerDriverConfig
from .......rerankers.methods import EnsembleFusionRerankerConfig, RetrieverConfig, SingleStepRerankerConfig

NGS_RERANKDRIVER_DEFAULT_CONFIG = RerankerDriverConfig(
    name='ensemble_fusion',
    strategy_config=EnsembleFusionRerankerConfig(
        vdb_names=['dense_triplets', 'bm25_triplets'],
        retriever_configs=[RetrieverConfig(fetch_n=50, threshold=None), RetrieverConfig(fetch_n=50, threshold=None)],
        weights=[0.7, 0.3]
    )
)

BSGS_RERANKDRIVER_DEFAULT_CONFIG = RerankerDriverConfig(
    name='single_step',
    strategy_config=SingleStepRerankerConfig(
        vdb_name='dense_triplets',
        threshold=0.5,
        fetch_n=25
    )
)
