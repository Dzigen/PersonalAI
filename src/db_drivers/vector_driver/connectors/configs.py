from ..utils import VectorDBConnectionConfig

DEFAULT_CHROMA_CONFIG = VectorDBConnectionConfig(
    params={"hnsw:space": "ip","hnsw:M": 4096},
    conn={'path':'../data/graph_structures/default_vectorstore'})

DEFAULT_MILVUS_CONFIG = VectorDBConnectionConfig(
    conn={'host': 'localhost', 'port': 19530, 'user': 'root', 'pass': 'Milvus'},
    db_info={'db': 'test_db', 'table': 'test_collection'},
    params={'id_length': 32, 'vector_dim': 1024, 'document_max_length': 51200, 'load': True,
            'flush': True, 'create_sleep': 1, 'search_metric': 'IP'})
