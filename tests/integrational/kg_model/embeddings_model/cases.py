import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
sys.path.insert(0, PROJECT_BASE_DIR)

from ..instances import SIMPLE_TRIPLET1, THESIS_TRIPLET2, EPISODIC_TRIPLET1, \
    EPISODIC_TRIPLET4, SIMPLE_TRIPLET2, SIMPLE_TRIPLET3, THESIS_TRIPLET1, \
        EPISODIC_TRIPLET2, EPISODIC_TRIPLET3, THESIS_TRIPLET3, SIMPLE_TRIPLET4, \
            SIMPLE_TRIPLET1_2, OBJECT_NODE1, OBJECT_NODE2, OBJECT_NODE3

# TO CHANGE
AVAILABLE_EMBEDDING_MODELS = ['chroma', 'inmemory', 'elasticsearch', 'opensearch', 'weaviate', 'qdrant']  # 'chroma', 'inmemory', 'elasticsearch', 'opensearch', 'weaviate', 'qdrant' | 'milvus'

# embeddings-model tests
# init_triplets, add_nodes_flag, expected_init_count, expected_creation_info
EM_CREATE_TEST_CASES = [
    # 1. пустой список
    [[], False, {'triplets': 0, 'nodes': 0},
        {'triplets': set(), 'nodes': set()}],
    # 2. добавление одного триплета
    # 2.1 simple
    [[SIMPLE_TRIPLET1], True, {'triplets': 1, 'nodes': 2},
     {'triplets': {SIMPLE_TRIPLET1.relation.id}, 'nodes': {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id}}],
    # 2.2 thesis
    [[THESIS_TRIPLET2], True, {'triplets': 1, 'nodes': 2},
     {'triplets': {THESIS_TRIPLET2.relation.id}, 'nodes': {THESIS_TRIPLET2.start_node.id, THESIS_TRIPLET2.end_node.id}}],
    # 2.3 episodic with object
    [[EPISODIC_TRIPLET1], True, {'triplets': 1, 'nodes': 2},
     {'triplets': {EPISODIC_TRIPLET1.relation.id}, 'nodes': {EPISODIC_TRIPLET1.start_node.id, EPISODIC_TRIPLET1.end_node.id}}],
    # 2.4 episodic with thesis
    [[EPISODIC_TRIPLET4], True, {'triplets': 1, 'nodes': 2},
     {'triplets': {EPISODIC_TRIPLET4.relation.id}, 'nodes': {EPISODIC_TRIPLET4.start_node.id, EPISODIC_TRIPLET4.end_node.id}}],
    # 3. добавление связанных триплетов (full, wo_sn, only_rel)
    # 3.1 simple rel
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET2, SIMPLE_TRIPLET3], True, {'triplets': 3, 'nodes': 3},
     {'triplets': {SIMPLE_TRIPLET1.relation.id, SIMPLE_TRIPLET2.relation.id, SIMPLE_TRIPLET3.relation.id},
      'nodes': {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id, SIMPLE_TRIPLET2.end_node.id}}],
    # 3.2 hyper (object with thesis)
    [[SIMPLE_TRIPLET1, THESIS_TRIPLET1, THESIS_TRIPLET2], True, {'triplets': 2, 'nodes': 3},
     {'triplets': {SIMPLE_TRIPLET1.relation.id, THESIS_TRIPLET1.relation.id, THESIS_TRIPLET2.relation.id},
      'nodes': {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id, THESIS_TRIPLET1.end_node.id}}],
    # 3.3 episodic (object with episodic)
    [[SIMPLE_TRIPLET1, EPISODIC_TRIPLET1, EPISODIC_TRIPLET2], True, {'triplets': 2, 'nodes': 3},
     {'triplets': {SIMPLE_TRIPLET1.relation.id, EPISODIC_TRIPLET1.relation.id, EPISODIC_TRIPLET2.relation.id},
      'nodes': {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id, EPISODIC_TRIPLET1.end_node.id}}],
    # 3.4 episodic (thesis with episodic)
    [[EPISODIC_TRIPLET3, THESIS_TRIPLET3, EPISODIC_TRIPLET4], True, {'triplets': 2, 'nodes': 3},
     {'triplets': {EPISODIC_TRIPLET3.relation.id, THESIS_TRIPLET3.relation.id, EPISODIC_TRIPLET4.relation.id},
      'nodes': {EPISODIC_TRIPLET3.start_node.id, EPISODIC_TRIPLET3.end_node.id, THESIS_TRIPLET3.end_node.id}}],
    # 4. добавление связанных триплетов (full, wo_en)
    # 4.1 object -[simple]> object
    [[SIMPLE_TRIPLET2, SIMPLE_TRIPLET1], True, {'triplets': 2, 'nodes': 3},
     {'triplets': {SIMPLE_TRIPLET2.relation.id, SIMPLE_TRIPLET1.relation.id},
      'nodes': {SIMPLE_TRIPLET2.start_node.id, SIMPLE_TRIPLET2.end_node.id, SIMPLE_TRIPLET1.start_node.id}}],
    # 4.2 object -[hyper]> thesis
    [[THESIS_TRIPLET2, THESIS_TRIPLET1], True, {'triplets': 1, 'nodes': 3},
     {'triplets': {THESIS_TRIPLET2.relation.id, THESIS_TRIPLET1.relation.id},
      'nodes': {THESIS_TRIPLET2.start_node.id, THESIS_TRIPLET2.end_node.id, THESIS_TRIPLET1.start_node.id}}],
    # 4.3 object -[episodic]> episodic
    [[EPISODIC_TRIPLET2, EPISODIC_TRIPLET1], True, {'triplets': 1, 'nodes': 3},
     {'triplets': {EPISODIC_TRIPLET2.relation.id, EPISODIC_TRIPLET1.relation.id},
      'nodes': {EPISODIC_TRIPLET2.start_node.id, EPISODIC_TRIPLET2.end_node.id, EPISODIC_TRIPLET1.start_node.id}}],
    # 4.4 thesis -[episodic]> episodic
    [[EPISODIC_TRIPLET3, EPISODIC_TRIPLET4], True, {'triplets': 1, 'nodes': 3},
     {'triplets': {EPISODIC_TRIPLET3.relation.id, EPISODIC_TRIPLET4.relation.id},
      'nodes': {EPISODIC_TRIPLET3.start_node.id, EPISODIC_TRIPLET3.end_node.id, EPISODIC_TRIPLET4.start_node.id}}],
    # 5. добавление связанных триплетов (full, wo_sn)
    # 5.1 object <[simple]- object
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET2], True, {'triplets': 2, 'nodes': 3},
     {'triplets': {SIMPLE_TRIPLET1.relation.id, SIMPLE_TRIPLET2.relation.id},
      'nodes': {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id, SIMPLE_TRIPLET2.end_node.id}}],
    # 5.2 thesis <[hyper]- object
    [[SIMPLE_TRIPLET1, THESIS_TRIPLET1], True, {'triplets': 2, 'nodes': 3},
     {'triplets': {SIMPLE_TRIPLET1.relation.id, THESIS_TRIPLET1.relation.id},
      'nodes': {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id, THESIS_TRIPLET1.end_node.id}}],
    # 5.3 episodic <[episodic]- object
    [[SIMPLE_TRIPLET1, EPISODIC_TRIPLET1], True, {'triplets': 2, 'nodes': 3},
     {'triplets': {SIMPLE_TRIPLET1.relation.id, EPISODIC_TRIPLET1.relation.id},
      'nodes': {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id, EPISODIC_TRIPLET1.end_node.id}}],
    # 5.4 episodic <[episodic]- thesis
    [[THESIS_TRIPLET3, EPISODIC_TRIPLET4], True, {'triplets': 2, 'nodes': 3},
     {'triplets': {THESIS_TRIPLET3.relation.id, EPISODIC_TRIPLET4.relation.id},
      'nodes': {THESIS_TRIPLET3.start_node.id, THESIS_TRIPLET3.end_node.id, EPISODIC_TRIPLET4.end_node.id}}],
    # 6. добавление несколько разных триплетов
    # 6.1 simple and simple
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET4], True, {'triplets': 2, 'nodes': 4},
     {'triplets': {SIMPLE_TRIPLET1.relation.id, SIMPLE_TRIPLET4.relation.id},
      'nodes': {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id, SIMPLE_TRIPLET4.start_node.id, SIMPLE_TRIPLET4.end_node.id}}],
    # 6.2 simple and hyper
    [[SIMPLE_TRIPLET1, THESIS_TRIPLET3], True, {'triplets': 2, 'nodes': 4},
     {'triplets': {SIMPLE_TRIPLET1.relation.id, THESIS_TRIPLET3.relation.id},
      'nodes': {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id, THESIS_TRIPLET3.start_node.id, THESIS_TRIPLET3.end_node.id}}],
    # 6.3 hyper and episodic
    [[THESIS_TRIPLET1, EPISODIC_TRIPLET2], True, {'triplets': 2, 'nodes': 4},
     {'triplets': {THESIS_TRIPLET1.relation.id, EPISODIC_TRIPLET2.relation.id},
      'nodes': {THESIS_TRIPLET1.start_node.id, THESIS_TRIPLET1.end_node.id, EPISODIC_TRIPLET2.start_node.id, EPISODIC_TRIPLET2.end_node.id}}],
    # 6.4 simple and episodic
    [[SIMPLE_TRIPLET4, EPISODIC_TRIPLET1], True, {'triplets': 2, 'nodes': 4},
     {'triplets': {SIMPLE_TRIPLET4.relation.id, EPISODIC_TRIPLET1.relation.id},
      'nodes': {SIMPLE_TRIPLET4.start_node.id, SIMPLE_TRIPLET4.end_node.id, EPISODIC_TRIPLET1.start_node.id, EPISODIC_TRIPLET1.end_node.id}}],
    # 7. добавление триплетов с одинаковыми строковыми представлениями
    # 7.1 simple
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET1], True, {'triplets': 1, 'nodes': 2},
     {'triplets': {SIMPLE_TRIPLET1.relation.id},
      'nodes': {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id}}],
    # 7.2 thesis
    [[THESIS_TRIPLET1, THESIS_TRIPLET2], True, {'triplets': 1, 'nodes': 3},
     {'triplets': {THESIS_TRIPLET1.relation.id},
      'nodes': {THESIS_TRIPLET1.start_node.id, THESIS_TRIPLET1.end_node.id, THESIS_TRIPLET2.start_node.id}}],
    # 7.3 episodic
    [[EPISODIC_TRIPLET1, EPISODIC_TRIPLET2], True, {'triplets': 1, 'nodes': 3},
     {'triplets': {EPISODIC_TRIPLET1.relation.id},
      'nodes': {EPISODIC_TRIPLET1.start_node.id, EPISODIC_TRIPLET1.end_node.id, EPISODIC_TRIPLET2.start_node.id}}]
]

EM_POPULATED_CREATE_TEST_CASES = []
for db_vendor in AVAILABLE_EMBEDDING_MODELS:
    for i in range(len(EM_CREATE_TEST_CASES)):
        EM_POPULATED_CREATE_TEST_CASES.append(
            EM_CREATE_TEST_CASES[i] + [db_vendor])

print("Количество порождённых тестов для EM_CREATE:",len(EM_POPULATED_CREATE_TEST_CASES))

###############################################################################################

# init_triplets, expected_creation_info, expected_init_count, triplets_to_delete, delete_info, expected_final_count, exception
EM_DELETE_TEST_CASES = [
    # 1. Удаление только связи
    [[SIMPLE_TRIPLET2, SIMPLE_TRIPLET3, SIMPLE_TRIPLET1_2],
     {'triplets': {SIMPLE_TRIPLET2.relation.id, SIMPLE_TRIPLET3.relation.id,
                   SIMPLE_TRIPLET1_2.relation.id}, 'nodes': {OBJECT_NODE1.id, OBJECT_NODE2.id, OBJECT_NODE3.id}},
     {'triplets': 3, 'nodes': 3}, [SIMPLE_TRIPLET1_2],
     {0: {'s_node': False, 'triplet': True, 'e_node': False}}, {'triplets': 2, 'nodes': 3}, False],
    # 2. Удаление связи и стартовой вершины
    [[SIMPLE_TRIPLET2, SIMPLE_TRIPLET3],
     {'triplets': {SIMPLE_TRIPLET2.relation.id, SIMPLE_TRIPLET3.relation.id},
         'nodes': {OBJECT_NODE1.id, OBJECT_NODE2.id, OBJECT_NODE3.id}},
     {'triplets': 2, 'nodes': 3}, [SIMPLE_TRIPLET2],
     {0: {'s_node': True, 'triplet': True, 'e_node': False}}, {'triplets': 1, 'nodes': 2}, False],
    # 3. Удаление связи и конечной вершины
    [[SIMPLE_TRIPLET2, SIMPLE_TRIPLET3],
     {'triplets': {SIMPLE_TRIPLET2.relation.id, SIMPLE_TRIPLET3.relation.id},
         'nodes': {OBJECT_NODE1.id, OBJECT_NODE2.id, OBJECT_NODE3.id}},
     {'triplets': 2, 'nodes': 3}, [SIMPLE_TRIPLET3],
     {0: {'s_node': False, 'triplet': True, 'e_node': True}}, {'triplets': 1, 'nodes': 2}, False],
    # 4. Удаление только конечной вершины
    [[SIMPLE_TRIPLET2, SIMPLE_TRIPLET3],
     {'triplets': {SIMPLE_TRIPLET2.relation.id, SIMPLE_TRIPLET3.relation.id},
         'nodes': {OBJECT_NODE1.id, OBJECT_NODE2.id, OBJECT_NODE3.id}},
     {'triplets': 2, 'nodes': 3}, [SIMPLE_TRIPLET3],
     {0: {'s_node': False, 'triplet': False, 'e_node': True}}, {'triplets': 2, 'nodes': 2}, False],
    # 5. Удаление только стартовой вершины
    [[SIMPLE_TRIPLET2, SIMPLE_TRIPLET3],
     {'triplets': {SIMPLE_TRIPLET2.relation.id, SIMPLE_TRIPLET3.relation.id},
         'nodes': {OBJECT_NODE1.id, OBJECT_NODE2.id, OBJECT_NODE3.id}},
     {'triplets': 2, 'nodes': 3}, [SIMPLE_TRIPLET2],
     {0: {'s_node': True, 'triplet': False, 'e_node': False}}, {'triplets': 2, 'nodes': 2}, False],
    # 6. удаление несколько разных триплетов
    [[SIMPLE_TRIPLET2, SIMPLE_TRIPLET3, SIMPLE_TRIPLET1_2],
     {'triplets': {SIMPLE_TRIPLET2.relation.id, SIMPLE_TRIPLET3.relation.id, SIMPLE_TRIPLET1_2.relation.id},
      'nodes': {OBJECT_NODE1.id, OBJECT_NODE2.id, OBJECT_NODE3.id}},
     {'triplets': 3, 'nodes': 3}, [SIMPLE_TRIPLET1_2, SIMPLE_TRIPLET2],
     {0: {'s_node': False, 'triplet': True, 'e_node': False},
         1: {'s_node': True, 'triplet': True, 'e_node': False}},
     {'triplets': 1, 'nodes': 2}, False],
    # 7. удаление несколько одинаковых триплетов
    [[SIMPLE_TRIPLET2, SIMPLE_TRIPLET3, SIMPLE_TRIPLET1_2],
     {'triplets': {SIMPLE_TRIPLET2.relation.id, SIMPLE_TRIPLET3.relation.id, SIMPLE_TRIPLET1_2.relation.id},
      'nodes': {OBJECT_NODE1.id, OBJECT_NODE2.id, OBJECT_NODE3.id}},
     {'triplets': 3, 'nodes': 3}, [SIMPLE_TRIPLET1_2, SIMPLE_TRIPLET1_2],
     {0: {'s_node': False, 'triplet': True, 'e_node': False},
         1: {'s_node': False, 'triplet': True, 'e_node': False}},
     {'triplets': 2, 'nodes': 3}, False]
]

EM_POPULATED_DELETE_TEST_CASES = []
for db_vendor in AVAILABLE_EMBEDDING_MODELS:
    for i in range(len(EM_DELETE_TEST_CASES)):
        EM_POPULATED_DELETE_TEST_CASES.append(
            EM_DELETE_TEST_CASES[i] + [db_vendor])

print("Количество порождённых тестов для EM_DELETE:",
      len(EM_POPULATED_DELETE_TEST_CASES))
