from ...utils import VectorDBConnectionConfig

DEFAULT_ELASTICSEARCH_BM25_CONFIG = VectorDBConnectionConfig(
    conn={'host': 'localhost', 'port': 9201},
)

DEFAULT_INMEMORY_BM25_CONFIG = VectorDBConnectionConfig(
    params={
        'save_on_disk': True,
        'rewrite': True
    }
)

DEFAULT_OPENSEARCH_BM25_CONFIG = VectorDBConnectionConfig(
    conn={'host': 'localhost', 'port': 9200, 'user': 'admin', 'pass': 'admin'}
)

DEFAULT_WEAVIATE_BM25_CONFIG = VectorDBConnectionConfig(
    conn={'host': 'localhost', 'port': 8083},
)
