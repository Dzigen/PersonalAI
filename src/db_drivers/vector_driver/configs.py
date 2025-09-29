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
        'opensearch': ...,  # TODO
        'elasticsearch': ...,  # TODO
        'inmemory': ...  # TODO
    }
}

AVAILABLE_VECTORDB_CONNECTORS = {
    'chroma': ChromaVectorConnection,
    'milvus': MilvusVectorConnector,
    'opensearch_bm25': OpenSeachBM25Connector,  # TODO
    'elasticsearch_bm25': ElasticSearchBM25Connector,  # TODO
    'inmemory_bm25': InMemoryBM25Connector  # TODO
}
