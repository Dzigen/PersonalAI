from typing import Dict


PAI_FILESTRUCTURE: Dict = {
    'directories': {
        'agent_stat': 'memory_parts/stat/agent',
        'cache': 'memory_parts/cache',
        'text2id': 'memory_parts/text2id',
        'graph_part': 'memory_parts/graph_model',
        'vectorized_nodes': 'memory_parts/embeddings_model/vectorized_nodes',
        'vectorized_triples': 'memory_parts/embeddings_model/vectorized_triples',
        'vectorized_tree_leafs': 'memory_parts/nodes_tree/vectorized_leafs',
        'vectorized_tree_summaries': 'memory_parts/nodes_tree/vectorized_summaries',
        'nodes_tree': 'memory_parts/nodes_tree/tree',
        'extracted_triples': 'tmp_extraxted_triples',
        'qa_traces': 'tmp_qa_traces',
        'setting': 'setting'
    },
    'configuration_files': {
        'required': {
            'personalai_partial_config': 'pai_partial_config.yaml',
            'kg_model_config': 'kg_model_config.yaml',
            'mem_pipeline_config': 'memorize_pipeline_config.yaml',
            'textidstore_config': 'textidstore_config.yaml'
        },
        'optional': {
            'qa_pipeline_config': 'qa_pipeline_config.yaml',
            'cache_kvdriver_config': 'cache_kvdriver_config_config.yaml',
            'inferencestat_config': 'inferencestat_config.yaml'
        }
    }
}