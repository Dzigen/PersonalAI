import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
sys.path.insert(0, PROJECT_BASE_DIR)

from .instances import SIMPLE_TRIPLET2, SIMPLE_TRIPLET1_2, SIMPLE_TRIPLET1, \
    SIMPLE_TRIPLET3, THESIS_TRIPLET1, THESIS_TRIPLET2

# TO CHANGE
AVAILABLE_GRAPH_MODELS = ['neo4j', 'kuzu', 'inmemory_graph', 'blazegraph', 'falkordb']  # 'neo4j', 'kuzu', 'inmemory_graph', 'blazegraph', 'falkordb'

AVAILABLE_EMBEDDING_MODELS = ['chroma', 'inmemory', 'elasticsearch', 'opensearch', 'weaviate', 'qdrant']  # 'chroma', 'inmemory', 'elasticsearch', 'opensearch', 'weaviate', 'qdrant' | 'milvus'


###############################################################################################

from .embeddings_model.cases import EM_CREATE_TEST_CASES
from .graph_model.cases import GM_CREATE_TEST_CASES

# triplets, expected_count, expected_graph_cinfo, expected_vector_cinfo
KG_CREATE_TEST_CASES = [
    [GM_T_CASE[0], {'graph_info': GM_T_CASE[1], 'embeddings_info': EM_T_CASE[2],
                    'nodestree_info': None}, GM_T_CASE[2], EM_T_CASE[3]]
    for EM_T_CASE, GM_T_CASE in zip(EM_CREATE_TEST_CASES, GM_CREATE_TEST_CASES)]

KG_POPULATED_CREATE_TEST_CASES = []
for vector_vendor in AVAILABLE_EMBEDDING_MODELS:
    for graph_vendor in AVAILABLE_GRAPH_MODELS:
        for i in range(len(KG_CREATE_TEST_CASES)):
            KG_POPULATED_CREATE_TEST_CASES.append(
                KG_CREATE_TEST_CASES[i] + [f"{vector_vendor}/{graph_vendor}"])

print("Количество порождённых тестов для KG_CREATE:",
      len(KG_POPULATED_CREATE_TEST_CASES))

# Note: Для разных трипелтов может быть одно векторное представление (нужно это проверять при удалении)

# init_triplets, expected_init_count, delete_triplets, expected_final_count, expected_graph_dinfo, expected_vector_dinfo
KG_DELETE_TEST_CASES = [
    # 1. Удаление всего триплета (один)
    [[SIMPLE_TRIPLET2], {'graph_info': {'triplets': 1, 'nodes': 2}, 'embeddings_info': {'triplets': 1, 'nodes': 2}, 'nodestree_info': None},
     [SIMPLE_TRIPLET2], {'graph_info': {'triplets': 0, 'nodes': 0}, 'embeddings_info': {'triplets': 0, 'nodes': 0}, 'nodestree_info': None},
        {0: {'s_node': True, 'e_node': True}},
        {0: {'s_node': True, 'triplet': True, 'e_node': True}}],
    # 2. Удаление всего триплета (несколько)
    # 2.1 одинаковые триплеты
    [[SIMPLE_TRIPLET1_2, SIMPLE_TRIPLET2], {'graph_info': {'triplets': 2, 'nodes': 3}, 'embeddings_info': {'triplets': 2, 'nodes': 3}, 'nodestree_info': None},
        [SIMPLE_TRIPLET1_2, SIMPLE_TRIPLET1_2], {'graph_info': {'triplets': 1, 'nodes': 2}, 'embeddings_info': {'triplets': 1, 'nodes': 2}, 'nodestree_info': None},
        {0: {'s_node': True, 'e_node': False}, 1: {
            's_node': False, 'e_node': False}},
        {0: {'s_node': True, 'triplet': True, 'e_node': False}, 1: {'s_node': False, 'triplet': False, 'e_node': False}}],
    # 2.2 разные триплеты
    [[SIMPLE_TRIPLET1_2, SIMPLE_TRIPLET2], {'graph_info': {'triplets': 2, 'nodes': 3}, 'embeddings_info': {'triplets': 2, 'nodes': 3}, 'nodestree_info': None},
        [SIMPLE_TRIPLET1_2, SIMPLE_TRIPLET2], {'graph_info': {'triplets': 0, 'nodes': 0}, 'embeddings_info': {'triplets': 0, 'nodes': 0}, 'nodestree_info': None},
        {0: {'s_node': True, 'e_node': False},1: {'s_node': True, 'e_node': True}},
        {0: {'s_node': True, 'triplet': True, 'e_node': False}, 1: {'s_node': True, 'triplet': True, 'e_node': True}}],
    # 3. Удаление только связи
    # 3.1 удаление связи из графовой бд и триплета из векторной
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET2, SIMPLE_TRIPLET3], {'graph_info': {'triplets': 3, 'nodes': 3}, 'embeddings_info': {'triplets': 3, 'nodes': 3}, 'nodestree_info': None},
        [SIMPLE_TRIPLET1], {'graph_info': {'triplets': 2, 'nodes': 3}, 'embeddings_info': {'triplets': 2, 'nodes': 3}, 'nodestree_info': None},
        {0: {'s_node': False, 'e_node': False}},
        {0: {'s_node': False, 'triplet': True, 'e_node': False}}],
    # 3.2 удаление связи из графовой бд, но не триплета из векторной
    [[THESIS_TRIPLET1, THESIS_TRIPLET2], {'graph_info': {'triplets': 2, 'nodes': 3}, 'embeddings_info': {"triplets": 1, 'nodes': 3}, 'nodestree_info': None},
        [THESIS_TRIPLET1], {'graph_info': {'triplets': 1, 'nodes': 2}, 'embeddings_info': {'triplets': 1, 'nodes': 2}, 'nodestree_info': None},
        {0: {'s_node': True, 'e_node': False}},
        {0: {'s_node': True, 'triplet': False, 'e_node': False}}],
    # 4. Удаление связи и конечной вершины
    [[SIMPLE_TRIPLET1_2, SIMPLE_TRIPLET2], {'graph_info': {'triplets': 2, 'nodes': 3}, 'embeddings_info': {'triplets': 2, 'nodes': 3}, 'nodestree_info': None},
        [SIMPLE_TRIPLET2], {'graph_info': {'triplets': 1, 'nodes': 2}, 'embeddings_info': {'triplets': 1, 'nodes': 2}, 'nodestree_info': None},
        {0: {'s_node': False, 'e_node': True}},
        {0: {'s_node': False, 'triplet': True, 'e_node': True}}]
]

KG_POPULATED_DELETE_TEST_CASES = []
for vector_vendor in AVAILABLE_EMBEDDING_MODELS:
    for graph_vendor in AVAILABLE_GRAPH_MODELS:
        for i in range(len(KG_DELETE_TEST_CASES)):
            KG_POPULATED_DELETE_TEST_CASES.append(
                KG_DELETE_TEST_CASES[i] + [f"{vector_vendor}/{graph_vendor}"])

print("Количество порождённых тестов для KG_DELETE:",
      len(KG_POPULATED_DELETE_TEST_CASES))

# init_triplets, expected_init_count
KG_CLEAR_TEST_CASES = [
    [GM_T_CASE[0], {'graph_info': GM_T_CASE[1],
                    'embeddings_info': EM_T_CASE[2]}]
    for GM_T_CASE, EM_T_CASE in zip(GM_CREATE_TEST_CASES, EM_CREATE_TEST_CASES)]

KG_POPULATED_CLEAR_TEST_CASES = []
for vector_vendor in AVAILABLE_EMBEDDING_MODELS:
    for graph_vendor in AVAILABLE_GRAPH_MODELS:
        for i in range(len(KG_CLEAR_TEST_CASES)):
            KG_POPULATED_CLEAR_TEST_CASES.append(
                KG_CLEAR_TEST_CASES[i] + [f"{vector_vendor}/{graph_vendor}"])

print("Количество порождённых тестов для KG_CLEAR:",
      len(KG_POPULATED_CLEAR_TEST_CASES))
