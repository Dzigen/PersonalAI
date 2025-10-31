from ...utils import VectorDBConnectionConfig

DEFAULT_CHROMA_CONFIG = VectorDBConnectionConfig(
    params={"hnsw:space": "ip", "hnsw:M": 4096},
    conn={'path': "./personalai_tmp/volumes/chroma"})

DEFAULT_MILVUS_CONFIG = VectorDBConnectionConfig(
    conn={'host': 'localhost', 'port': 19530,
          'user': 'root', 'pass': 'Milvus'},
    params={'id_length': 32, 'vector_dim': 1024, 'document_max_length': 51200, 'load': True,
            'flush': True, 'create_sleep': 1.5, 'search_metric': 'IP'})
