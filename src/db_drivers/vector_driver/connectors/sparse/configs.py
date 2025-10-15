from ...utils import VectorDBConnectionConfig

DEFAULT_ELASTICSEARCH_BM25_CONFIG = VectorDBConnectionConfig(
    conn={'host': 'localhost', 'port': 9201},
)

DEFAULT_INMEMORY_BM25_CONFIG = VectorDBConnectionConfig(
    params={
        'load_from_disk': False,
        'load_dump_dir': "./personalai_tmp/volumes/inmemory_bm25",
        'save_on_disk': True,
        'save_dump_dir': "./personalai_tmp/volumes/inmemory_bm25"
    }
)

DEFAULT_OPENSEARCH_BM25_CONFIG = VectorDBConnectionConfig(
    conn={'host': 'localhost', 'port': 9200, 'user': 'admin', 'pass': 'admin'}
)

DEFAULT_WEAVIATE_BM25_CONFIG = VectorDBConnectionConfig(
    conn={'host': 'localhost', 'port': 8083},
)
