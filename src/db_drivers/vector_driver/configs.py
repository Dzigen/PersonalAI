from .connectors.dense import MilvusVectorConnector, ChromaVectorConnection
from .connectors.dense.configs import DEFAULT_CHROMA_CONFIG, DEFAULT_MILVUS_CONFIG

from .connectors.sparse import OpenSeachBM25Connector, ElasticSearchBM25Connector, InMemoryBM25Connector
from .connectors.sparse.configs import DEFAULT_INMEMORY_BM25_CONFIG, DEFAULT_ELASTICSEARCH_BM25_CONFIG, \
    DEFAULT_OPENSEARCH_BM25_CONFIG

DEFAULT_VECTORDB_CONFIGS = {
    'dense': {
        'chroma': DEFAULT_CHROMA_CONFIG,
        'milvus': DEFAULT_MILVUS_CONFIG
    },
    'sparse_bm25': {
        'opensearch': DEFAULT_OPENSEARCH_BM25_CONFIG,
        'elasticsearch': DEFAULT_ELASTICSEARCH_BM25_CONFIG,
        # 'weaviate': DEFAULT_WEAVIATE_BM25_CONFIG,
        'inmemory': DEFAULT_INMEMORY_BM25_CONFIG
    }
}

AVAILABLE_VECTORDB_CONNECTORS = {
    'chroma': ChromaVectorConnection,
    'milvus': MilvusVectorConnector,
    'opensearch_bm25': OpenSeachBM25Connector,
    'elasticsearch_bm25': ElasticSearchBM25Connector,
    'inmemory_bm25': InMemoryBM25Connector,
    # 'weaviate_bm25': WeaviateBM25Connector
}
