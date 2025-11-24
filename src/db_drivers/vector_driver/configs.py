from typing import Dict

from .connectors.dense import ChromaVectorConnection, InMemoryVectorConnector, \
    ElasticSearchVectorConnector, OpenSeachVectorConnector, QdrantVectorConnector  # , MilvusVectorConnector, WeaviateVectorConnector
from .connectors.dense.configs import DEFAULT_CHROMA_CONFIG, DEFAULT_INMEMORY_CONFIG, \
    DEFAULT_ELASTICSEARCH_CONFIG, DEFAULT_OPENSEARCH_CONFIG, DEFAULT_QDRANT_CONFIG  # ,DEFAULT_MILVUS_CONFIG, DEFAULT_WEAVIATE_CONFIG

from .connectors.sparse import OpenSeachBM25Connector, ElasticSearchBM25Connector, InMemoryBM25Connector, WeaviateBM25Connector
from .connectors.sparse.configs import DEFAULT_INMEMORY_BM25_CONFIG, DEFAULT_ELASTICSEARCH_BM25_CONFIG, \
    DEFAULT_OPENSEARCH_BM25_CONFIG, DEFAULT_WEAVIATE_BM25_CONFIG

from .utils import AbstractVectorDatabaseConnection, VectorDBConnectionConfig

DEFAULT_VECTORDB_CONFIGS: Dict[str, Dict[str, VectorDBConnectionConfig]] = {
    'dense': {
        'chroma': DEFAULT_CHROMA_CONFIG,
        # 'milvus': DEFAULT_MILVUS_CONFIG,
        'elasticsearch': DEFAULT_ELASTICSEARCH_CONFIG,
        'inmemory': DEFAULT_INMEMORY_CONFIG,
        'openseach': DEFAULT_OPENSEARCH_CONFIG,
        'qdrant': DEFAULT_QDRANT_CONFIG
        # 'weaviate': DEFAULT_WEAVIATE_CONFIG
    },
    'sparse_bm25': {
        'opensearch': DEFAULT_OPENSEARCH_BM25_CONFIG,
        'elasticsearch': DEFAULT_ELASTICSEARCH_BM25_CONFIG,
        'weaviate': DEFAULT_WEAVIATE_BM25_CONFIG,
        'inmemory': DEFAULT_INMEMORY_BM25_CONFIG
    }
}

AVAILABLE_VECTORDB_CONNECTORS: Dict[str, AbstractVectorDatabaseConnection] = {
    'chroma': ChromaVectorConnection,
    # 'milvus': MilvusVectorConnector,
    'inmemory': InMemoryVectorConnector,
    'elasticsearch': ElasticSearchVectorConnector,
    'opensearch': OpenSeachVectorConnector,
    'qdrant': QdrantVectorConnector,
    # 'weaviate': WeaviateVectorConnector,

    'opensearch_bm25': OpenSeachBM25Connector,
    'elasticsearch_bm25': ElasticSearchBM25Connector,
    'inmemory_bm25': InMemoryBM25Connector,
    'weaviate_bm25': WeaviateBM25Connector
}
