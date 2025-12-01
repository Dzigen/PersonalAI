import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
sys.path.insert(0, PROJECT_BASE_DIR)

from ..instances import SIMPLE_TRIPLET1, THESIS_TRIPLET2, EPISODIC_TRIPLET1, \
    EPISODIC_TRIPLET4, SIMPLE_TRIPLET2, SIMPLE_TRIPLET3, THESIS_TRIPLET1, \
        EPISODIC_TRIPLET2, EPISODIC_TRIPLET3, THESIS_TRIPLET3, SIMPLE_TRIPLET4, \
            SIMPLE_TRIPLET1_2, EPISODIC_TRIPLET5, EPISODIC_TRIPLET6, EPISODIC_TRIPLET7, \
              EPISODIC_TRIPLET8, THESIS_TRIPLET4

from src.utils.data_structs import RelationType, NodeType

# TO CHANGE
AVAILABLE_GRAPH_MODELS = ['neo4j']  # 'inmemory_graph', 'neo4j', 'kuzu', 'blazegraph'

# graph-model tests
# init_triplets, expected_init_count, expected_create_info
GM_CREATE_TEST_CASES = [
    # 1. пустой список
    [[], {'triplets': 0, 'nodes': 0}, {'triplets': dict(), 'nodes': dict()}],
    # 2. добавление одного триплета
    # 2.1 simple
    [[SIMPLE_TRIPLET1], {'triplets': 1, 'nodes': 2},
     {'triplets': {RelationType.simple: {SIMPLE_TRIPLET1.id}},
      'nodes': {NodeType.object: {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id}}}],
    # 2.2 thesis
    [[THESIS_TRIPLET2], {'triplets': 1, 'nodes': 2},
     {'triplets': {RelationType.hyper: {THESIS_TRIPLET2.id}},
      'nodes': {NodeType.object: {THESIS_TRIPLET2.start_node.id}, NodeType.hyper: {THESIS_TRIPLET2.end_node.id}}}],
    # 2.3 episodic with object
    [[EPISODIC_TRIPLET1], {'triplets': 1, 'nodes': 2},
     {'triplets': {RelationType.episodic: {EPISODIC_TRIPLET1.id}},
      'nodes': {NodeType.object: {EPISODIC_TRIPLET1.start_node.id}, NodeType.episodic: {EPISODIC_TRIPLET1.end_node.id}}}],
    # 2.4 episodic with thesis
    [[EPISODIC_TRIPLET4], {'triplets': 1, 'nodes': 2},
     {'triplets': {RelationType.episodic: {EPISODIC_TRIPLET4.id}},
      'nodes': {NodeType.hyper: {EPISODIC_TRIPLET4.start_node.id}, NodeType.episodic: {EPISODIC_TRIPLET4.end_node.id}}}],
    # 3. добавление связанных триплетов (full, wo_sn, only_rel)
    # 3.1 simple rel
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET2, SIMPLE_TRIPLET3], {'triplets': 3, 'nodes': 3},
     {'triplets': {RelationType.simple: {SIMPLE_TRIPLET1.id, SIMPLE_TRIPLET2.id, SIMPLE_TRIPLET3.id}},
      'nodes': {NodeType.object: {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id, SIMPLE_TRIPLET2.end_node.id}}}],
    # 3.2 hyper (object with thesis)
    [[SIMPLE_TRIPLET1, THESIS_TRIPLET1, THESIS_TRIPLET2], {'triplets': 3, 'nodes': 3},
     {'triplets': {RelationType.simple: {SIMPLE_TRIPLET1.id}, RelationType.hyper: {THESIS_TRIPLET1.id, THESIS_TRIPLET2.id}},
      'nodes': {NodeType.object: {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id}, NodeType.hyper: {THESIS_TRIPLET1.end_node.id}}}],
    # 3.3 episodic (object with episodic)
    [[SIMPLE_TRIPLET1, EPISODIC_TRIPLET1, EPISODIC_TRIPLET2], {'triplets': 3, 'nodes': 3},
     {'triplets': {RelationType.simple: {SIMPLE_TRIPLET1.id}, RelationType.episodic: {EPISODIC_TRIPLET1.id, EPISODIC_TRIPLET2.id}},
      'nodes': {NodeType.object: {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id}, NodeType.episodic: {EPISODIC_TRIPLET1.end_node.id}}}],
    # 3.4 episodic (thesis with episodic)
    [[EPISODIC_TRIPLET3, THESIS_TRIPLET3, EPISODIC_TRIPLET4],  {'triplets': 3, 'nodes': 3},
     {'triplets': {RelationType.episodic: {EPISODIC_TRIPLET3.id, EPISODIC_TRIPLET4.id}, RelationType.hyper: {THESIS_TRIPLET3.id}},
      'nodes': {NodeType.object: {EPISODIC_TRIPLET3.start_node.id}, NodeType.episodic: {EPISODIC_TRIPLET3.end_node.id}, NodeType.hyper: {THESIS_TRIPLET3.end_node.id}}}],
    # 4. добавление связанных триплетов (full, wo_en)
    # 4.1 object -[simple]> object
    [[SIMPLE_TRIPLET2, SIMPLE_TRIPLET1], {'triplets': 2, 'nodes': 3},
     {'triplets': {RelationType.simple: {SIMPLE_TRIPLET2.id, SIMPLE_TRIPLET1.id}},
      'nodes': {NodeType.object: {SIMPLE_TRIPLET2.start_node.id, SIMPLE_TRIPLET2.end_node.id, SIMPLE_TRIPLET1.start_node.id}}}],
    # 4.2 object -[hyper]> thesis
    [[THESIS_TRIPLET2, THESIS_TRIPLET1], {'triplets': 2, 'nodes': 3},
     {'triplets': {RelationType.hyper: {THESIS_TRIPLET2.id, THESIS_TRIPLET1.id}},
      'nodes': {NodeType.object: {THESIS_TRIPLET2.start_node.id, THESIS_TRIPLET1.start_node.id}, NodeType.hyper: {THESIS_TRIPLET2.end_node.id}}}],
    # 4.3 object -[episodic]> episodic
    [[EPISODIC_TRIPLET2, EPISODIC_TRIPLET1], {'triplets': 2, 'nodes': 3},
     {'triplets': {RelationType.episodic: {EPISODIC_TRIPLET2.id, EPISODIC_TRIPLET1.id}},
      'nodes': {NodeType.object: {EPISODIC_TRIPLET2.start_node.id, EPISODIC_TRIPLET1.start_node.id}, NodeType.episodic: {EPISODIC_TRIPLET2.end_node.id}}}],
    # 4.4 thesis -[episodic]> episodic
    [[EPISODIC_TRIPLET3, EPISODIC_TRIPLET4], {'triplets': 2, 'nodes': 3},
     {'triplets': {RelationType.episodic: {EPISODIC_TRIPLET3.id, EPISODIC_TRIPLET4.id}},
      'nodes': {NodeType.object: {EPISODIC_TRIPLET3.start_node.id}, NodeType.hyper: {EPISODIC_TRIPLET4.start_node.id}, NodeType.episodic: {EPISODIC_TRIPLET3.end_node.id}}}],
    # 5. добавление связанных триплетов (full, wo_sn)
    # 5.1 object <[simple]- object
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET2], {'triplets': 2, 'nodes': 3},
     {'triplets': {RelationType.simple: {SIMPLE_TRIPLET1.id, SIMPLE_TRIPLET2.id}},
      'nodes': {NodeType.object: {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id, SIMPLE_TRIPLET2.end_node.id}}}],
    # 5.2 thesis <[hyper]- object
    [[SIMPLE_TRIPLET1, THESIS_TRIPLET1], {'triplets': 2, 'nodes': 3},
     {'triplets': {RelationType.simple: {SIMPLE_TRIPLET1.id}, RelationType.hyper: {THESIS_TRIPLET1.id}},
      'nodes': {NodeType.object: {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id}, NodeType.hyper: {THESIS_TRIPLET1.end_node.id}}}],
    # 5.3 episodic <[episodic]- object
    [[SIMPLE_TRIPLET1, EPISODIC_TRIPLET1], {'triplets': 2, 'nodes': 3},
     {'triplets': {RelationType.simple: {SIMPLE_TRIPLET1.id}, RelationType.episodic: {EPISODIC_TRIPLET1.id}},
      'nodes': {NodeType.object: {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id}, NodeType.episodic: {EPISODIC_TRIPLET1.end_node.id}}}],
    # 5.4 episodic <[episodic]- thesis
    [[THESIS_TRIPLET3, EPISODIC_TRIPLET4], {'triplets': 2, 'nodes': 3},
     {'triplets': {RelationType.hyper: {THESIS_TRIPLET3.id}, RelationType.episodic: {EPISODIC_TRIPLET4.id}},
      'nodes': {NodeType.object: {THESIS_TRIPLET3.start_node.id}, NodeType.hyper: {THESIS_TRIPLET3.end_node.id}, NodeType.episodic: {EPISODIC_TRIPLET4.end_node.id}}}],
    # 6. добавление несколько разных триплетов
    # 6.1 simple and simple
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET4], {'triplets': 2, 'nodes': 4},
     {'triplets': {RelationType.simple: {SIMPLE_TRIPLET1.id, SIMPLE_TRIPLET4.id}},
      'nodes': {NodeType.object: {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id, SIMPLE_TRIPLET4.start_node.id, SIMPLE_TRIPLET4.end_node.id}}}],
    # 6.2 simple and hyper
    [[SIMPLE_TRIPLET1, THESIS_TRIPLET3], {'triplets': 2, 'nodes': 4},
     {'triplets': {RelationType.simple: {SIMPLE_TRIPLET1.id}, RelationType.hyper: {THESIS_TRIPLET3.id}},
      'nodes': {NodeType.object: {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id, THESIS_TRIPLET3.start_node.id}, NodeType.hyper: {THESIS_TRIPLET3.end_node.id}}}],
    # 6.3 hyper and episodic
    [[THESIS_TRIPLET1, EPISODIC_TRIPLET2], {'triplets': 2, 'nodes': 4},
     {'triplets': {RelationType.hyper: {THESIS_TRIPLET1.id}, RelationType.episodic: {EPISODIC_TRIPLET2.id}},
      'nodes': {NodeType.object: {THESIS_TRIPLET1.start_node.id, EPISODIC_TRIPLET2.start_node.id}, NodeType.hyper: {THESIS_TRIPLET1.end_node.id}, NodeType.episodic: {EPISODIC_TRIPLET2.end_node.id}}}],
    # 6.4 simple and episodic
    [[SIMPLE_TRIPLET4, EPISODIC_TRIPLET1], {'triplets': 2, 'nodes': 4},
     {'triplets': {RelationType.simple: {SIMPLE_TRIPLET4.id}, RelationType.episodic: {EPISODIC_TRIPLET1.id}},
      'nodes': {NodeType.object: {SIMPLE_TRIPLET4.start_node.id, SIMPLE_TRIPLET4.end_node.id, EPISODIC_TRIPLET1.start_node.id}, NodeType.episodic: {EPISODIC_TRIPLET1.end_node.id}}}],
    # 7. добавление триплетов с одинаковыми строковыми представлениями
    # 7.1 simple
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET1], {'triplets': 1, 'nodes': 2},
     {'triplets': {RelationType.simple: {SIMPLE_TRIPLET1.id}},
      'nodes': {NodeType.object: {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id}}}],
    # 7.2 thesis
    [[THESIS_TRIPLET1, THESIS_TRIPLET2], {'triplets': 2, 'nodes': 3},
     {'triplets': {RelationType.hyper: {THESIS_TRIPLET1.id, THESIS_TRIPLET2.id}},
      'nodes': {NodeType.object: {THESIS_TRIPLET1.start_node.id, THESIS_TRIPLET2.start_node.id}, NodeType.hyper: {THESIS_TRIPLET1.end_node.id}}}],
    # 7.3 episodic
    [[EPISODIC_TRIPLET1, EPISODIC_TRIPLET2], {'triplets': 2, 'nodes': 3},
     {'triplets': {RelationType.episodic: {EPISODIC_TRIPLET1.id, EPISODIC_TRIPLET2.id}},
      'nodes': {NodeType.object: {EPISODIC_TRIPLET1.start_node.id, EPISODIC_TRIPLET2.start_node.id}, NodeType.episodic: {EPISODIC_TRIPLET1.end_node.id}}}],
    #8. Добавление триплетов, у которых вершины разного типа имеют одинаковое строковое представление
    #8.1 (object[same_str])->(episodic) ; (hyper[same_str])->(episodic)
    [[EPISODIC_TRIPLET5, EPISODIC_TRIPLET6], {'triplets': 2, 'nodes': 3},
     {'triplets': {RelationType.episodic: {EPISODIC_TRIPLET5.id, EPISODIC_TRIPLET6.id}},
      'nodes': {NodeType.object: {EPISODIC_TRIPLET5.start_node.id}, NodeType.hyper: {EPISODIC_TRIPLET6.start_node.id}, NodeType.episodic: {EPISODIC_TRIPLET5.end_node.id}}}],
    # 8.2 (hyper)->(episodic)
    [[EPISODIC_TRIPLET7], {'triplets': 1, 'nodes': 2},
     {'triplets': {RelationType.episodic: {EPISODIC_TRIPLET7.id}},
      'nodes': {NodeType.hyper: {EPISODIC_TRIPLET7.start_node.id}, NodeType.episodic: {EPISODIC_TRIPLET7.end_node.id}}}],
    # 8.3 (object)->(episodic)
    [[EPISODIC_TRIPLET8], {'triplets': 1, 'nodes': 2},
     {'triplets': {RelationType.episodic: {EPISODIC_TRIPLET8.id}},
      'nodes': {NodeType.object: {EPISODIC_TRIPLET8.start_node.id}, NodeType.episodic: {EPISODIC_TRIPLET8.end_node.id}}}],
    # 8.4 (object)->(hyper)
    [[THESIS_TRIPLET4], {'triplets': 1, 'nodes': 2},
     {'triplets': {RelationType.hyper: {THESIS_TRIPLET4.id}},
      'nodes': {NodeType.object: {THESIS_TRIPLET4.start_node.id}, NodeType.hyper: {THESIS_TRIPLET4.end_node.id}}}]
]

GM_POPULATED_CREATE_TEST_CASES = []
for db_vendor in AVAILABLE_GRAPH_MODELS:
    for i in range(len(GM_CREATE_TEST_CASES)):
        GM_POPULATED_CREATE_TEST_CASES.append(
            GM_CREATE_TEST_CASES[i] + [db_vendor])

print("Количество порождённых тестов для GM_CREATE:",len(GM_POPULATED_CREATE_TEST_CASES))

###############################################################################################

# init_triplets, expected_create_info, expected_init_count, triplets_to_delete,
# expected_delete_ginfo, expected_final_count, expected_delete_vinfo
GM_DELETE_TEST_CASES = [
    # 1. Удаление всего триплета (один)
    [[SIMPLE_TRIPLET2], {'triplets': {RelationType.simple: {SIMPLE_TRIPLET2.id}}, 'nodes': {NodeType.object: {SIMPLE_TRIPLET2.start_node.id, SIMPLE_TRIPLET2.end_node.id}}},
     {'triplets': 1, 'nodes': 2}, [SIMPLE_TRIPLET2], {0: {'s_node': True, 'e_node': True}},
        {'triplets': 0, 'nodes': 0}, {0: {'s_node': True, 'triplet': True, 'e_node': True}}],
    # 2. Удаление всего триплета (несколько)
    # 2.1 одинаковые триплеты
    [[SIMPLE_TRIPLET1_2, SIMPLE_TRIPLET2],
        {'triplets': {RelationType.simple: {SIMPLE_TRIPLET2.id, SIMPLE_TRIPLET1_2.id}},
         'nodes': {NodeType.object: {SIMPLE_TRIPLET1_2.start_node.id, SIMPLE_TRIPLET1_2.end_node.id, SIMPLE_TRIPLET2.end_node.id}}},
        {'triplets': 2, 'nodes': 3}, [SIMPLE_TRIPLET1_2, SIMPLE_TRIPLET1_2],
        {0: {'s_node': True, 'e_node': False}, 1: {'s_node': False, 'e_node': False}},
        {'triplets': 1, 'nodes': 2}, {0: {'s_node': True, 'triplet': True, 'e_node': False}, 1: {'s_node': False, 'triplet': False, 'e_node': False}}],
    # 2.2 разные триплеты
    [[SIMPLE_TRIPLET1_2, SIMPLE_TRIPLET2],
        {'triplets': {RelationType.simple: {SIMPLE_TRIPLET2.id, SIMPLE_TRIPLET1_2.id}},
         'nodes': {NodeType.object: {SIMPLE_TRIPLET1_2.start_node.id, SIMPLE_TRIPLET1_2.end_node.id, SIMPLE_TRIPLET2.end_node.id}}},
        {'triplets': 2, 'nodes': 3}, [SIMPLE_TRIPLET1_2, SIMPLE_TRIPLET2],
        {0: {'s_node': True, 'e_node': False}, 1: {'s_node': True, 'e_node': True}},
        {'triplets': 0, 'nodes': 0}, {0: {'s_node': True, 'triplet': True, 'e_node': False}, 1: {'s_node': True, 'triplet': True, 'e_node': True}}],
    # 3. Удаление только связи
    # 3.1 удаление связи из графовой бд и триплета из векторной
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET2, SIMPLE_TRIPLET3],
        {'triplets': {RelationType.simple: {SIMPLE_TRIPLET1.id, SIMPLE_TRIPLET2.id, SIMPLE_TRIPLET3.id}},
         'nodes': {NodeType.object: {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id, SIMPLE_TRIPLET2.end_node.id}}},
        {'triplets': 3, 'nodes': 3}, [SIMPLE_TRIPLET1],
        {0: {'s_node': False, 'e_node': False}}, {'triplets': 2, 'nodes': 3},
        {0: {'s_node': False, 'triplet': True, 'e_node': False}}],
    # 3.2 удаление связи из графовой бд, но не триплета из векторной
    [[THESIS_TRIPLET1, THESIS_TRIPLET2],
        {'triplets': {RelationType.hyper: {THESIS_TRIPLET1.id, THESIS_TRIPLET2.id}}, 'nodes': {
            NodeType.object: {THESIS_TRIPLET1.start_node.id, THESIS_TRIPLET2.start_node.id}, NodeType.hyper: {THESIS_TRIPLET1.end_node.id}}},
        {'triplets': 2, 'nodes': 3}, [THESIS_TRIPLET1],
        {0: {'s_node': True, 'e_node': False}}, {'triplets': 1, 'nodes': 2},
        {0: {'s_node': True, 'triplet': False, 'e_node': False}}],
    # 4. Удаление связи и конечной вершины
    [[SIMPLE_TRIPLET1_2, SIMPLE_TRIPLET2],
        {'triplets': {RelationType.simple: {SIMPLE_TRIPLET2.id, SIMPLE_TRIPLET1_2.id}},
         'nodes': {NodeType.object: {SIMPLE_TRIPLET1_2.start_node.id, SIMPLE_TRIPLET1_2.end_node.id, SIMPLE_TRIPLET2.end_node.id}}},
        {'triplets': 2, 'nodes': 3}, [SIMPLE_TRIPLET2],
        {0: {'s_node': False, 'e_node': True}},
        {'triplets': 1, 'nodes': 2}, {0: {'s_node': False, 'triplet': True, 'e_node': True}}],
    # 5. Удаление триплета с дублирующимся строковым представлением у существующей вершины, но с другим типом
    [[EPISODIC_TRIPLET5, EPISODIC_TRIPLET6],
     {'triplets': {RelationType.episodic: {EPISODIC_TRIPLET5.id, EPISODIC_TRIPLET6.id}},
      'nodes': {NodeType.object: {EPISODIC_TRIPLET5.start_node.id}, NodeType.hyper: {EPISODIC_TRIPLET6.start_node.id}, NodeType.episodic: {EPISODIC_TRIPLET5.end_node.id}}},
      {'triplets': 2, 'nodes': 3}, [EPISODIC_TRIPLET6], {0: {'s_node': True, 'e_node': False}},
      {'triplets': 1, 'nodes': 2}, {0: {'s_node': True, 'triplet': False, 'e_node': False}}
    ],
]

GM_POPULATED_DELETE_TEST_CASES = []
for db_vendor in AVAILABLE_GRAPH_MODELS:
    for i in range(len(GM_DELETE_TEST_CASES)):
        GM_POPULATED_DELETE_TEST_CASES.append(
            GM_DELETE_TEST_CASES[i] + [db_vendor])

print("Количество порождённых тестов для GM_DELETE:",
      len(GM_POPULATED_DELETE_TEST_CASES))
