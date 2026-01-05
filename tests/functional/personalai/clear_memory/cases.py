import sys
from copy import deepcopy
# TO CHANGE
PROJECT_BASE_DIR = '../'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.utils.data_structs import Triplet, Node, Relation, NodeType, RelationType

# TO CHANGE
AVAILABLE_GRAPH_MODELS = ['neo4j', 'kuzu', 'inmemory_graph', 'blazegraph', 'falkordb']  # 'neo4j', 'kuzu', 'inmemory_graph', 'blazegraph', 'falkordb'
AVAILABLE_EMBEDDING_MODELS = ['chroma', 'inmemory', 'elasticsearch', 'opensearch', 'weaviate', 'qdrant']  # 'chroma', 'inmemory', 'elasticsearch', 'opensearch', 'weaviate', 'qdrant'
AVAILABLE_KVID_STORES = ['inmemory_kv', 'redis', 'mongo', 'mixed_kv'] # 'inmemory_kv', 'redis', 'mongo', 'mixed_kv'

###############################################################################################

OBJECT_NODE1 = Node(id="onode1", name="onode1", type=NodeType.object)
OBJECT_NODE2 = Node(id="onode2", name="onode2", type=NodeType.object)
OBJECT_NODE3 = Node(id="onode3", name="onode3", type=NodeType.object)
OBJECT_NODE4 = Node(id="onode4", name="onode4", type=NodeType.object)

SIMPLE_RELATION1 = Relation(id='srel1',name='simple', type=RelationType.simple)
SIMPLE_RELATION2 = Relation(id='srel2',name='simple', type=RelationType.simple)
SIMPLE_RELATION3 = Relation(id='srel3',name='simple', type=RelationType.simple)


SIMPLE_TRIPLET1 = Triplet(id='st1', start_node=OBJECT_NODE1, relation=SIMPLE_RELATION1, end_node=OBJECT_NODE2)
SIMPLE_TRIPLET2 = Triplet(id='st2', start_node=OBJECT_NODE2, relation=SIMPLE_RELATION2, end_node=OBJECT_NODE3)
SIMPLE_TRIPLET3 = Triplet(id='st3', start_node=OBJECT_NODE3, relation=SIMPLE_RELATION3, end_node=OBJECT_NODE4)

###############################################################################################

TRIPLET_GROUP1 = {'123': [SIMPLE_TRIPLET1, SIMPLE_TRIPLET2], '456': [SIMPLE_TRIPLET3]}
EXPECTED_PRE_MEMSIZE1 = {
    'graph_info': {
        'nodes': {
            NodeType.object.value: 4, NodeType.hyper.value: 0,
            NodeType.episodic.value: 0, NodeType.time.value: 0},
        'triplets': {
            RelationType.simple.value: 3, RelationType.hyper.value: 0,
            RelationType.episodic.value: 0, RelationType.time.value: 0}
    },
    'embeddings_info': {
        'nodes': {
            NodeType.object.value: {'dense_nodes': 4},
            NodeType.hyper.value: {'dense_nodes': 0},
            NodeType.episodic.value: {'dense_nodes': 0},
            NodeType.time.value: {'dense_nodes': 0}
        },
        'triplets': {
            'dense_triplets': 3
        }
    },
    'nodestree_info': None
}
TEXTIDS_TO_DELETE1 = ['123']
EXPECTED_POST_MEMSIZE1 = {
    'graph_info': {
        'nodes': {
            NodeType.object.value: 2, NodeType.hyper.value: 0,
            NodeType.episodic.value: 0, NodeType.time.value: 0},
        'triplets': {
            RelationType.simple.value: 1, RelationType.hyper.value: 0,
            RelationType.episodic.value: 0, RelationType.time.value: 0}
    },
    'embeddings_info': {
        'nodes': {
            NodeType.object.value: {'dense_nodes': 2},
            NodeType.hyper.value: {'dense_nodes': 0},
            NodeType.episodic.value: {'dense_nodes': 0},
            NodeType.time.value: {'dense_nodes': 0}
        },
        'triplets': {
            'dense_triplets': 1
        }
    },
    'nodestree_info': None
}

TRIPLET_GROUP2 = deepcopy(TRIPLET_GROUP1)
EXPECTED_PRE_MEMSIZE2 = deepcopy(EXPECTED_PRE_MEMSIZE1)
TEXTIDS_TO_DELETE2 = ['456']
EXPECTED_POST_MEMSIZE2 = {
    'graph_info': {
        'nodes': {
            NodeType.object.value: 3, NodeType.hyper.value: 0,
            NodeType.episodic.value: 0, NodeType.time.value: 0},
        'triplets': {
            RelationType.simple.value: 2, RelationType.hyper.value: 0,
            RelationType.episodic.value: 0, RelationType.time.value: 0}
    },
    'embeddings_info': {
        'nodes': {
            NodeType.object.value: {'dense_nodes': 3},
            NodeType.hyper.value: {'dense_nodes': 0},
            NodeType.episodic.value: {'dense_nodes': 0},
            NodeType.time.value: {'dense_nodes': 0}
        },
        'triplets': {
            'dense_triplets': 2
        }
    },
    'nodestree_info': None
}

TRIPLET_GROUP3 = {'123': [SIMPLE_TRIPLET2], '456': [SIMPLE_TRIPLET1, SIMPLE_TRIPLET3]}
EXPECTED_PRE_MEMSIZE3 = deepcopy(EXPECTED_PRE_MEMSIZE1)
TEXTIDS_TO_DELETE3 = ['123']
EXPECTED_POST_MEMSIZE3 = {
    'graph_info': {
        'nodes': {
            NodeType.object.value: 4, NodeType.hyper.value: 0,
            NodeType.episodic.value: 0, NodeType.time.value: 0},
        'triplets': {
            RelationType.simple.value: 2, RelationType.hyper.value: 0,
            RelationType.episodic.value: 0, RelationType.time.value: 0}
    },
    'embeddings_info': {
        'nodes': {
            NodeType.object.value: {'dense_nodes': 4},
            NodeType.hyper.value: {'dense_nodes': 0},
            NodeType.episodic.value: {'dense_nodes': 0},
            NodeType.time.value: {'dense_nodes': 0}
        },
        'triplets': {
            'dense_triplets': 2
        }
    },
    'nodestree_info': None
}

TRIPLET_GROUP4 = {'123': [SIMPLE_TRIPLET1], '456': [SIMPLE_TRIPLET3]}
EXPECTED_PRE_MEMSIZE4 = {
    'graph_info': {
        'nodes': {
            NodeType.object.value: 4, NodeType.hyper.value: 0,
            NodeType.episodic.value: 0, NodeType.time.value: 0},
        'triplets': {
            RelationType.simple.value: 2, RelationType.hyper.value: 0,
            RelationType.episodic.value: 0, RelationType.time.value: 0}
    },
    'embeddings_info': {
        'nodes': {
            NodeType.object.value: {'dense_nodes': 4},
            NodeType.hyper.value: {'dense_nodes': 0},
            NodeType.episodic.value: {'dense_nodes': 0},
            NodeType.time.value: {'dense_nodes': 0}
        },
        'triplets': {
            'dense_triplets': 2
        }
    },
    'nodestree_info': None
}
TEXTIDS_TO_DELETE4 = ['123']
EXPECTED_POST_MEMSIZE4 = {
    'graph_info': {
        'nodes': {
            NodeType.object.value: 2, NodeType.hyper.value: 0,
            NodeType.episodic.value: 0, NodeType.time.value: 0},
        'triplets': {
            RelationType.simple.value: 1, RelationType.hyper.value: 0,
            RelationType.episodic.value: 0, RelationType.time.value: 0}
    },
    'embeddings_info': {
        'nodes': {
            NodeType.object.value: {'dense_nodes': 2},
            NodeType.hyper.value: {'dense_nodes': 0},
            NodeType.episodic.value: {'dense_nodes': 0},
            NodeType.time.value: {'dense_nodes': 0}
        },
        'triplets': {
            'dense_triplets': 1
        }
    },
    'nodestree_info': None
}

TRIPLET_GROUP5 = {'123': [SIMPLE_TRIPLET1, SIMPLE_TRIPLET2], '456': [SIMPLE_TRIPLET2, SIMPLE_TRIPLET3]}
EXPECTED_PRE_MEMSIZE5 = {
    'graph_info': {
        'nodes': {
            NodeType.object.value: 4, NodeType.hyper.value: 0,
            NodeType.episodic.value: 0, NodeType.time.value: 0},
        'triplets': {
            RelationType.simple.value: 3, RelationType.hyper.value: 0,
            RelationType.episodic.value: 0, RelationType.time.value: 0}
    },
    'embeddings_info': {
        'nodes': {
            NodeType.object.value: {'dense_nodes': 4},
            NodeType.hyper.value: {'dense_nodes': 0},
            NodeType.episodic.value: {'dense_nodes': 0},
            NodeType.time.value: {'dense_nodes': 0}
        },
        'triplets': {
            'dense_triplets': 3
        }
    },
    'nodestree_info': None
}
TEXTIDS_TO_DELETE5 = ['123']
EXPECTED_POST_MEMSIZE5 = {
    'graph_info': {
        'nodes': {
            NodeType.object.value: 3, NodeType.hyper.value: 0,
            NodeType.episodic.value: 0, NodeType.time.value: 0},
        'triplets': {
            RelationType.simple.value: 2, RelationType.hyper.value: 0,
            RelationType.episodic.value: 0, RelationType.time.value: 0}
    },
    'embeddings_info': {
        'nodes': {
            NodeType.object.value: {'dense_nodes': 3},
            NodeType.hyper.value: {'dense_nodes': 0},
            NodeType.episodic.value: {'dense_nodes': 0},
            NodeType.time.value: {'dense_nodes': 0}
        },
        'triplets': {
            'dense_triplets': 2
        }
    },
    'nodestree_info': None
}

TRIPLET_GROUP21 = {'123': [SIMPLE_TRIPLET1, SIMPLE_TRIPLET2], '456': [SIMPLE_TRIPLET1], '789': [SIMPLE_TRIPLET3]}
EXPECTED_PRE_MEMSIZE21 = {
    'graph_info': {
        'nodes': {
            NodeType.object.value: 4, NodeType.hyper.value: 0,
            NodeType.episodic.value: 0, NodeType.time.value: 0},
        'triplets': {
            RelationType.simple.value: 3, RelationType.hyper.value: 0,
            RelationType.episodic.value: 0, RelationType.time.value: 0}
    },
    'embeddings_info': {
        'nodes': {
            NodeType.object.value: {'dense_nodes': 4},
            NodeType.hyper.value: {'dense_nodes': 0},
            NodeType.episodic.value: {'dense_nodes': 0},
            NodeType.time.value: {'dense_nodes': 0}
        },
        'triplets': {
            'dense_triplets': 3
        }
    },
    'nodestree_info': None
}
TEXTIDS_TO_DELETE21 = ['123', '456']
EXPECTED_POST_MEMSIZE21 = {
    'graph_info': {
        'nodes': {
            NodeType.object.value: 2, NodeType.hyper.value: 0,
            NodeType.episodic.value: 0, NodeType.time.value: 0},
        'triplets': {
            RelationType.simple.value: 1, RelationType.hyper.value: 0,
            RelationType.episodic.value: 0, RelationType.time.value: 0}
    },
    'embeddings_info': {
        'nodes': {
            NodeType.object.value: {'dense_nodes': 2},
            NodeType.hyper.value: {'dense_nodes': 0},
            NodeType.episodic.value: {'dense_nodes': 0},
            NodeType.time.value: {'dense_nodes': 0}
        },
        'triplets': {
            'dense_triplets': 1
        }
    },
    'nodestree_info': None
}

TRIPLET_GROUP22 = {'123': [SIMPLE_TRIPLET1, SIMPLE_TRIPLET2], '456': [SIMPLE_TRIPLET3]}
EXPECTED_PRE_MEMSIZE22 = deepcopy(EXPECTED_PRE_MEMSIZE21)
TEXTIDS_TO_DELETE22 = ['123', '456']
EXPECTED_POST_MEMSIZE22 = {
    'graph_info': {
        'nodes': {
            NodeType.object.value: 0, NodeType.hyper.value: 0,
            NodeType.episodic.value: 0, NodeType.time.value: 0},
        'triplets': {
            RelationType.simple.value: 0, RelationType.hyper.value: 0,
            RelationType.episodic.value: 0, RelationType.time.value: 0}
    },
    'embeddings_info': {
        'nodes': {
            NodeType.object.value: {'dense_nodes': 0},
            NodeType.hyper.value: {'dense_nodes': 0},
            NodeType.episodic.value: {'dense_nodes': 0},
            NodeType.time.value: {'dense_nodes': 0}
        },
        'triplets': {
            'dense_triplets': 0
        }
    },
    'nodestree_info': None
}

TRIPLET_GROUP23 = deepcopy(TRIPLET_GROUP22)
EXPECTED_PRE_MEMSIZE23 = deepcopy(EXPECTED_PRE_MEMSIZE21)
TEXTIDS_TO_DELETE23 = ['456', '123']
EXPECTED_POST_MEMSIZE23 = deepcopy(EXPECTED_POST_MEMSIZE22)

TRIPLET_GROUP24 = {'123': [SIMPLE_TRIPLET2, SIMPLE_TRIPLET3], '456': [SIMPLE_TRIPLET1]}
EXPECTED_PRE_MEMSIZE24 = deepcopy(EXPECTED_PRE_MEMSIZE21)
TEXTIDS_TO_DELETE24 = ['123', '456']
EXPECTED_POST_MEMSIZE24 = deepcopy(EXPECTED_POST_MEMSIZE22)

TRIPLET_GROUP25 = {'123': [SIMPLE_TRIPLET2, SIMPLE_TRIPLET3], '456': [SIMPLE_TRIPLET1]}
EXPECTED_PRE_MEMSIZE25 = deepcopy(EXPECTED_PRE_MEMSIZE21)
TEXTIDS_TO_DELETE25 = ['456', '123']
EXPECTED_POST_MEMSIZE25 = deepcopy(EXPECTED_POST_MEMSIZE22)

###############################################################################################

# triplet_groups_to_create, expected_pre_memorysize, textids_to_delete, expected_post_memorysize, personalai_inst
CLEARMEMORY_TEST_CASES = [
    # 1. Удаление триплетов по одному text_id
    # 1.1. (object)-[simple]->(object)
    # 1.1.1. удаление стартовой вершины и связи
    [TRIPLET_GROUP1, EXPECTED_PRE_MEMSIZE1, TEXTIDS_TO_DELETE1, EXPECTED_POST_MEMSIZE1],
    # 1.1.2. удаление конечной вершины и связи
    [TRIPLET_GROUP2, EXPECTED_PRE_MEMSIZE2, TEXTIDS_TO_DELETE2, EXPECTED_POST_MEMSIZE2],
    # 1.1.3. удаление только связи
    [TRIPLET_GROUP3, EXPECTED_PRE_MEMSIZE3, TEXTIDS_TO_DELETE3, EXPECTED_POST_MEMSIZE3],
    # 1.1.4. удаление триплета цилеком
    [TRIPLET_GROUP4, EXPECTED_PRE_MEMSIZE4, TEXTIDS_TO_DELETE4, EXPECTED_POST_MEMSIZE4],
    # 1.1.5. триплет никак не изменяется
    [TRIPLET_GROUP5, EXPECTED_PRE_MEMSIZE5, TEXTIDS_TO_DELETE5, EXPECTED_POST_MEMSIZE5],
    # 1.2. (object)-[hyper]->(hyper)
    # TODO
    # 1.3. (object)-[episodic]->(episodic)
    # TODO
    # 1.4. (hyper)-[episodic]->(episodic)
    # TODO
    # 2. Последовательное удаление трипелтов по нескольким text_id
    # 2.1. сначала триплет остаётся без изменений, а потом удаляется полностью
    # (триплет принадлежит обоим text_id)
    [TRIPLET_GROUP21, EXPECTED_PRE_MEMSIZE21, TEXTIDS_TO_DELETE21, EXPECTED_POST_MEMSIZE21],
    # 2.2. сначала удаляется стартовая вершина и связь, а потом конечная вершина
    # (конечная вершина принадлежит обоим text_id)
    [TRIPLET_GROUP22, EXPECTED_PRE_MEMSIZE22, TEXTIDS_TO_DELETE22, EXPECTED_POST_MEMSIZE22],
    # 2.3. сначала триплет остаётся без изменений, а потом удаляется полностью
    # (конечная вершина принадлежит обоим text_id)
    [TRIPLET_GROUP23, EXPECTED_PRE_MEMSIZE23, TEXTIDS_TO_DELETE23, EXPECTED_POST_MEMSIZE23],
    # 2.4. сначала удаляется конечная вершина и связь, а потом стартовая вершина
    # (стартовая вершина принадлежит обоим text_id)
    [TRIPLET_GROUP24, EXPECTED_PRE_MEMSIZE24, TEXTIDS_TO_DELETE24, EXPECTED_POST_MEMSIZE24],
    # 2.5. сначала триплет остаётся без изменений, а потом удаляется полностью
    # (стартовая вершина принадлежит обоим text_id)
    [TRIPLET_GROUP25, EXPECTED_PRE_MEMSIZE25, TEXTIDS_TO_DELETE25, EXPECTED_POST_MEMSIZE25],
]

POPULATED_CLEARMEMORY_TEST_CASES = []
for vector_vendor in AVAILABLE_EMBEDDING_MODELS:
    for graph_vendor in AVAILABLE_GRAPH_MODELS:
        for kvid_store in AVAILABLE_KVID_STORES:
            for i in range(len(CLEARMEMORY_TEST_CASES)):
                POPULATED_CLEARMEMORY_TEST_CASES.append(
                    CLEARMEMORY_TEST_CASES[i] + [f"{vector_vendor}/{graph_vendor}|{kvid_store}"])

print("Количество порождённых тестов для CLEAR_MEMORY: ", len(POPULATED_CLEARMEMORY_TEST_CASES))
