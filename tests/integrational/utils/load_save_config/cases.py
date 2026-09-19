from .conftest import AVAILABLE_CONFIGS


ZERO_NESTED_CONFIGS = [
    AVAILABLE_CONFIGS['db']['graph']['conn'],
    AVAILABLE_CONFIGS['db']['kv']['conn'],
    AVAILABLE_CONFIGS['db']['table']['conn'],
    AVAILABLE_CONFIGS['db']['tree']['conn'],
    AVAILABLE_CONFIGS['db']['vector']['conn'],

    AVAILABLE_CONFIGS['agent']['conn'],

    # AVAILABLE_CONFIGS['rerankers']['single_step'],
    # AVAILABLE_CONFIGS['rerankers']['multi_step'],
    # AVAILABLE_CONFIGS['rerankers']['ensemble'],

    AVAILABLE_CONFIGS['mem_pipeline']['updator']['agent_tasks'],
    AVAILABLE_CONFIGS['mem_pipeline']['extractor']['agent_tasks'],

    AVAILABLE_CONFIGS['kg_model']['tree']['agent_tasks'],

    AVAILABLE_CONFIGS['qa_pipeline']['preprocessor']['decompose']['agent_tasks'],
    AVAILABLE_CONFIGS['qa_pipeline']['preprocessor']['enhance']['agent_tasks'],
    AVAILABLE_CONFIGS['qa_pipeline']['preprocessor']['denoise']['agent_tasks'],

    AVAILABLE_CONFIGS['qa_pipeline']['aggregator']['agent_tasks'],

    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['graph_traversal']['astarmetrics'],
    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['graph_traversal']['bfs'],
    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['graph_traversal']['watercircles'],

    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['weak']['generator']['agent_tasks'],
    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['weak']['parser']['agent_tasks'],

    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['medium']['answr_gen']['agent_tasks'],
    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['medium']['cluea_summ']['agent_tasks'],
    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['medium']['cluea_gen']['agent_tasks'],
    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['medium']['clueq_gen']['agent_tasks'],
    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['medium']['entities']['agent_tasks'],
    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['medium']['plan_enh']['agent_tasks'],
    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['medium']['entities']['agent_tasks'],
    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['medium']['plan_enh']['agent_tasks']
]

ONE_NESTED_CONFIGS = [
    AVAILABLE_CONFIGS['db']['graph']['driver'],
    AVAILABLE_CONFIGS['db']['kv']['driver'],
    AVAILABLE_CONFIGS['db']['table']['driver'],
    AVAILABLE_CONFIGS['db']['tree']['driver'],
    AVAILABLE_CONFIGS['db']['vector']['driver'],

    AVAILABLE_CONFIGS['agent']['driver'],

    #AVAILABLE_CONFIGS['rerankers']['driver'],

    AVAILABLE_CONFIGS['mem_pipeline']['updator']['main'],
    AVAILABLE_CONFIGS['mem_pipeline']['extractor']['main'],

    AVAILABLE_CONFIGS['qa_pipeline']['preprocessor']['decompose']['main'],
    AVAILABLE_CONFIGS['qa_pipeline']['preprocessor']['enhance']['main'],
    AVAILABLE_CONFIGS['qa_pipeline']['preprocessor']['denoise']['main'],

    AVAILABLE_CONFIGS['qa_pipeline']['aggregator']['main'],

    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['graph_traversal']['astar'],

    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['weak']['generator']['main'],
    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['weak']['parser']['main'],

    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['medium']['answr_gen']['main'],
    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['medium']['cluea_summ']['main'],
    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['medium']['cluea_gen']['main'],
    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['medium']['clueq_gen']['main'],
    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['medium']['entities']['main'],
    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['medium']['plan_enh']['main']
]

TWO_NESTED_CONFIGS = [
    AVAILABLE_CONFIGS['stat_analyzer'],

    AVAILABLE_CONFIGS['mem_pipeline']['main'],

    AVAILABLE_CONFIGS['textidstore'],

    AVAILABLE_CONFIGS['kg_model']['tree']['main'],
    AVAILABLE_CONFIGS['kg_model']['embedder'],
    AVAILABLE_CONFIGS['kg_model']['graph'],

    AVAILABLE_CONFIGS['qa_pipeline']['preprocessor']['main'],

    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['graph_filtering']['naive'],
    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['graph_traversal']['beamsearch'],
    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['graph_traversal']['naiveretriever'],

    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['weak']['comparator'],

    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['medium']['matching']
]

THREE_NESTED_CONFIGS = [
    AVAILABLE_CONFIGS['kg_model']['main'],

    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['graph_traversal']['mixture']
]

FOUR_NESTED_CONFIGS = [
    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['weak']['retriever']
]

FIVE_NESTED_CONFIGS = [
    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['weak']['main'],
    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['medium']['main']
]

SIX_NESTED_CONFIGS = [
    AVAILABLE_CONFIGS['qa_pipeline']['reasoner']['main']
]

SEVEN_NESTED_CONFIGS = [
    AVAILABLE_CONFIGS['main']
]
