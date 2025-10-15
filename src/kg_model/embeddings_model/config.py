from ...db_drivers.vector_driver import VectorDBConnectionConfig, VectorDriverConfig

NODES_DB_DEFAULT_DRIVER_CONFIGS_MAPPING = {
    'nodes_dense': VectorDriverConfig(
        db_vendor='chroma', db_config=VectorDBConnectionConfig(
            params={"hnsw:space": "ip", "hnsw:M": 4096},
            conn={'path': "./personalai_tmp/memory_parts/embeddings_model/vectorized_nodes/chroma/default_densedb"},
            db_info={'db': 'default_db', 'table': "dense_nodes"},
            need_to_clear=False
        )
    ),
    'nodes_sparse_bm25': VectorDriverConfig(
        db_vendor='inmemory', vector_category='sparse_bm25', db_config=VectorDBConnectionConfig(
            db_info={'db': 'default_db', 'table': "sparsebm25_nodes"},
            params={'store_dump_name': 'inmemory_bm25', 'load_from_disk': True,
                    'load_dump_dir': "./personalai_tmp/memory_parts/embeddings_model/vectorized_nodes/inmemory_bm25", 'save_on_disk': True,
                    'save_dump_dir': "./personalai_tmp/memory_parts/embeddings_model/vectorized_nodes/inmemory_bm25"},
            need_to_clear=False
        )
    ),
}

TRIPLETS_DB_DEFAULT_DRIVER_CONFIGS_MAPPING = {
    'triplets_dense': VectorDriverConfig(
        db_vendor='chroma', db_config=VectorDBConnectionConfig(
            params={"hnsw:space": "ip", "hnsw:M": 4096},
            conn={'path': "./personalai_tmp/memory_parts/embeddings_model/vectorized_triplets/chroma/default_densedb"},
            db_info={'db': 'default_db', 'table': "vectorized_triplets"},
            need_to_clear=False
        )
    ),
    'triplets_sparse_bm25': VectorDriverConfig(
        db_vendor='inmemory', vector_category='sparse_bm25', db_config=VectorDBConnectionConfig(
            db_info={'db': 'default_db', 'table': "sparsebm25_triplets"},
            params={'store_dump_name': 'inmemory_bm25', 'load_from_disk': True,
                    'load_dump_dir': "./personalai_tmp/memory_parts/embeddings_model/vectorized_triplets/inmemory_bm25", 'save_on_disk': True,
                    'save_dump_dir': "./personalai_tmp/memory_parts/embeddings_model/vectorized_triplets/inmemory_bm25"},
            need_to_clear=False
        )
    )
}

EMBEDDINGS_MODEL_LOG_PATH = 'log/kg_model/embeddings'
