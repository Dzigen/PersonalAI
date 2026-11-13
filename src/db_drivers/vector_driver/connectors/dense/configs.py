from ...utils import VectorDBConnectionConfig

DEFAULT_CHROMA_CONFIG = VectorDBConnectionConfig(
    params={"hnsw:space": "ip", "hnsw:M": 4096},
)

DEFAULT_MILVUS_CONFIG = VectorDBConnectionConfig(
    conn={'host': 'localhost', 'port': 19530,
          'user': 'root', 'pass': 'Milvus'},
    params={
        'id_length': 32,  
        'vector_dim': 1024, # !!! PAY ATTENTION !!!
        'document_max_length': 51200, 
        'load': True,
        'flush': True, 
        'create_sleep': 1, 
        'search_metric': 'IP'
    }
)

DEFAULT_INMEMORY_CONFIG = VectorDBConnectionConfig(
    params={
        'save_on_disk': True,
        'vector_dim': 1024, # !!! PAY ATTENTION !!!
        'rewrite': True
    }
)

DEFAULT_ELASTICSEARCH_CONFIG = VectorDBConnectionConfig(
    conn={'host': 'localhost', 'port': 9201}
)

DEFAULT_WEAVIATE_CONFIG = VectorDBConnectionConfig(
    conn={'host': 'localhost', 'port': 8083},
)

DEFAULT_OPENSEARCH_CONFIG = VectorDBConnectionConfig(
    conn={'host': 'localhost', 'port': 9200, 'user': 'admin', 'pass': 'admin'},
    params={
        'vector_dim': 1024, # !!! PAY ATTENTION !!!
        'search_metric': 'innerproduct'
    }
)

DEFAULT_QDRANT_CONFIG = VectorDBConnectionConfig(
    conn={'host': 'localhost', 'port': 6333},
    params={
        'vector_dim': 1024, # !!! PAY ATTENTION !!!
        'search_metric': 'Dot'
    }
)
