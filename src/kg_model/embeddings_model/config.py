from ...db_drivers.vector_driver import VectorDBConnectionConfig, VectorDriverConfig

NODES_DB_DEFAULT_DRIVER_CONFIGS_MAPPING = {
    'nodes_dense': VectorDriverConfig(
        db_vendor='chroma', db_config=VectorDBConnectionConfig(
            params={"hnsw:space": "ip", "hnsw:M": 4096},
            conn={'path': "./personalai_tmp/graph_structures/vectorized_nodes/chroma/default_densedb"},
            db_info={'db': 'default_db', 'table': "dense_nodes"})),

    'nodes_sparse_bm25': VectorDriverConfig(
        db_vendor='inmemory', vector_category='sparse_bm25', db_config=VectorDBConnectionConfig(
            db_info={'db': 'default_db', 'table': "sparsebm25_nodes"})),
}

TRIPLETS_DB_DEFAULT_DRIVER_CONFIGS_MAPPING = {
    'triplets_dense': VectorDriverConfig(
        db_vendor='chroma', db_config=VectorDBConnectionConfig(
            params={"hnsw:space": "ip", "hnsw:M": 4096},
            conn={'path': "./personalai_tmp/graph_structures/vectorized_triplets/chroma/default_densedb"},
            db_info={'db': 'default_db', 'table': "vectorized_triplets"}))
}

EMBEDDINGS_MODEL_LOG_PATH = 'log/kg_model/embeddings'
