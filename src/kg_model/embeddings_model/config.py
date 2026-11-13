from ...db_drivers.vector_driver import VectorDBConnectionConfig, VectorDriverConfig

NODES_DB_DEFAULT_DRIVER_CONFIGS_MAPPING = {
    'dense_nodes': VectorDriverConfig(
        db_vendor='chroma', db_config=VectorDBConnectionConfig(
            params={"hnsw:space": "ip", "hnsw:M": 4096},
            db_info={'db': 'default_db', 'table': "dense_nodes", 'expected_db_base_path': './personalai_tmp'},
            need_to_clear=False
        )
    ),
    'bm25_nodes': VectorDriverConfig(
        db_vendor='inmemory', vector_category='sparse_bm25', db_config=VectorDBConnectionConfig(
            db_info={'db': 'default_db', 'table': "sparsebm25_nodes", 'expected_db_base_path': './personalai_tmp'},
            params={'save_on_disk': True, 'rewrite': True},
            need_to_clear=False
        )
    ),
}

TRIPLETS_DB_DEFAULT_DRIVER_CONFIGS_MAPPING = {
    'dense_triplets': VectorDriverConfig(
        db_vendor='chroma', db_config=VectorDBConnectionConfig(
            params={"hnsw:space": "ip", "hnsw:M": 4096},
            db_info={'db': 'default_db', 'table': "vectorized_triplets", 'expected_db_base_path': './personalai_tmp'},
            need_to_clear=False
        )
    ),
    'bm25_triplets': VectorDriverConfig(
        db_vendor='inmemory', vector_category='sparse_bm25', db_config=VectorDBConnectionConfig(
            db_info={'db': 'default_db', 'table': "sparsebm25_triplets", 'expected_db_base_path': './personalai_tmp'},
            params={'save_on_disk': True, 'rewrite': True},
            need_to_clear=False
        )
    )
}

EMBEDDINGS_MODEL_LOG_PATH = 'log/kg_model/embeddings'
