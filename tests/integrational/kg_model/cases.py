import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.utils.data_structs import Triplet, NodeCreator, Relation, RelationType, NodeType, TripletCreator
from src.utils.errors import ReturnInfo


# TO CHANGE
AVAILABLE_GRAPH_MODELS = ['inmemory_graph', 'neo4j', 'kuzu']

# TO CHANGE
AVAILABLE_EMBEDDING_MODELS = ['chroma']

###############################################################################################

# nodes
OBJECT_NODE1 = NodeCreator.create(name='abc', n_type=NodeType.object, prop={'k1': 'v1'})
OBJECT_NODE2 = NodeCreator.create(name='def', n_type=NodeType.object, prop={'k2': 'v2'})
OBJECT_NODE3 = NodeCreator.create(name='ghi', n_type=NodeType.object, prop={'k3': 'v3'})
OBJECT_NODE4 = NodeCreator.create(name='yhn', n_type=NodeType.object, prop={'k13': 'v13'})

THESIS_NODE1 = NodeCreator.create(name='qwerty', n_type=NodeType.hyper, prop={'k4': 'v4'})
THESIS_NODE2 = NodeCreator.create(name='asdfgh', n_type=NodeType.hyper, prop={'k5': 'v5'})
THESIS_NODE3 = NodeCreator.create(name='zxcvbn', n_type=NodeType.hyper, prop={'k6': 'v6'})

EPISODIC_NODE1 = NodeCreator.create(name='uiop', n_type=NodeType.episodic, prop={'k7': 'v7'})
EPISODIC_NODE2 = NodeCreator.create(name='jkl', n_type=NodeType.episodic, prop={'k8': 'v8'})
EPISODIC_NODE3 = NodeCreator.create(name='mnbv', n_type=NodeType.episodic, prop={'k9': 'v9'})

# triplets
SIMPLE_TRIPLET1 = TripletCreator.create(start_node=OBJECT_NODE1, relation=Relation(name='simple1', type=RelationType.simple, prop={'k10': 'v10'}), end_node=OBJECT_NODE2)
SIMPLE_TRIPLET1_2 = TripletCreator.create(start_node=OBJECT_NODE1, relation=Relation(name='simple1_1', type=RelationType.simple, prop={'k16': 'v16'}), end_node=OBJECT_NODE2)

SIMPLE_TRIPLET2 = TripletCreator.create(start_node=OBJECT_NODE2, relation=Relation(name='simple2', type=RelationType.simple, prop={'k11': 'v11'}), end_node=OBJECT_NODE3)
SIMPLE_TRIPLET3 = TripletCreator.create(start_node=OBJECT_NODE3, relation=Relation(name='simple3', type=RelationType.simple, prop={'k12': 'v12'}), end_node=OBJECT_NODE1)
SIMPLE_TRIPLET4 = TripletCreator.create(start_node=OBJECT_NODE3, relation=Relation(name='simple4', type=RelationType.simple, prop={'k14': 'v14'}), end_node=OBJECT_NODE4)
SIMPLE_TRIPLET5 = TripletCreator.create(start_node=OBJECT_NODE1, relation=Relation(name='simple5', type=RelationType.simple, prop={'k15': 'v15'}), end_node=OBJECT_NODE1)


THESIS_TRIPLET1 = TripletCreator.create(start_node=OBJECT_NODE1, relation=Relation(name='hyper', type=RelationType.hyper), end_node=THESIS_NODE1)
THESIS_TRIPLET2 = TripletCreator.create(start_node=OBJECT_NODE2, relation=Relation(name='hyper', type=RelationType.hyper), end_node=THESIS_NODE1)
THESIS_TRIPLET3 = TripletCreator.create(start_node=OBJECT_NODE3, relation=Relation(name='hyper', type=RelationType.hyper), end_node=THESIS_NODE2)


EPISODIC_TRIPLET1 = TripletCreator.create(start_node=OBJECT_NODE1, relation=Relation(name='episodic', type=RelationType.episodic), end_node=EPISODIC_NODE1)
EPISODIC_TRIPLET2 = TripletCreator.create(start_node=OBJECT_NODE2, relation=Relation(name='episodic', type=RelationType.episodic), end_node=EPISODIC_NODE1)
EPISODIC_TRIPLET3 = TripletCreator.create(start_node=OBJECT_NODE3, relation=Relation(name='episodic', type=RelationType.episodic), end_node=EPISODIC_NODE2)
EPISODIC_TRIPLET4 = TripletCreator.create(start_node=THESIS_NODE2, relation=Relation(name='episodic', type=RelationType.episodic), end_node=EPISODIC_NODE2)

###############################################################################################

# embeddings-model tests
# init_triplets, add_nodes_flag, expected_init_count, expected_creation_info
EM_CREATE_TEST_CASES = [
    # 1. пустой список
    [[], False, {'triplets': 0, 'nodes': 0}, {'triplets': set(), 'nodes': set()}],
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
    [[EPISODIC_TRIPLET3, THESIS_TRIPLET3,EPISODIC_TRIPLET4], True, {'triplets': 2, 'nodes': 3},
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
        EM_POPULATED_CREATE_TEST_CASES.append(EM_CREATE_TEST_CASES[i] + [db_vendor])

print("Количество порождённых тестов для EM_CREATE:", len(EM_POPULATED_CREATE_TEST_CASES))

###############################################################################################

# init_triplets, expected_creation_info, expected_init_count, triplets_to_delete, delete_info, expected_final_count
EM_DELETE_TEST_CASES = [
    # 1. Удаление всего триплета
    # 1.1. Все объекты присутствуют
    # 1.2. Присутвтует только связь
    # 1.3. Присутствует только связи + начальная вершина
    # 1.4. Присутствует только связи + конеченая вершина
    # 2. Удаление связи и стартовой вершины
    # 2.1. Все объекты присутствуют
    # 2.2. Присутствует только связь
    # 3. Удаление связи и конеченой вершины
    # 3.1. Все объекты присутствутю
    # 3.2. Присутствует только связь
    # 4. Удаление только связи
    # 5. Удаление смешанного набора
    # 5.1 Удаление всего триплета + связи и стартовой вершины + связи и конеченой вершины
]

EM_POPULATED_DELETE_TEST_CASES = []
for db_vendor in AVAILABLE_EMBEDDING_MODELS:
    for i in range(len(EM_DELETE_TEST_CASES)):
        EM_POPULATED_DELETE_TEST_CASES.append(EM_DELETE_TEST_CASES[i] + [db_vendor])

print("Количество порождённых тестов для EM_DELETE:", len(EM_POPULATED_DELETE_TEST_CASES))

###############################################################################################

# graph-model tests
# init_triplets, expected_init_count, expected_create_info
GM_CREATE_TEST_CASES = [
    # 1. пустой список
    [[], {'triplets': 0, 'nodes': 0}, {'triplets': set(), 'nodes': set()}],
    # 2. добавление одного триплета
    # 2.1 simple
    [[SIMPLE_TRIPLET1], {'triplets': 1, 'nodes': 2},
     {'triplets': {SIMPLE_TRIPLET1.id},
      'nodes': {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id}}],
    # 2.2 thesis
    [[THESIS_TRIPLET2], {'triplets': 1, 'nodes': 2},
     {'triplets': {THESIS_TRIPLET2.id},
      'nodes': {THESIS_TRIPLET2.start_node.id, THESIS_TRIPLET2.end_node.id}}],
    # 2.3 episodic with object
    [[EPISODIC_TRIPLET1], {'triplets': 1, 'nodes': 2},
     {'triplets': {EPISODIC_TRIPLET1.id},
      'nodes': {EPISODIC_TRIPLET1.start_node.id, EPISODIC_TRIPLET1.end_node.id}}],
    # 2.4 episodic with thesis
    [[EPISODIC_TRIPLET4], {'triplets': 1, 'nodes': 2},
     {'triplets': {EPISODIC_TRIPLET4.id},
      'nodes': {EPISODIC_TRIPLET4.start_node.id, EPISODIC_TRIPLET4.end_node.id}}],
    # 3. добавление связанных триплетов (full, wo_sn, only_rel)
    # 3.1 simple rel
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET2, SIMPLE_TRIPLET3], {'triplets': 3, 'nodes': 3},
     {'triplets': {SIMPLE_TRIPLET1.id, SIMPLE_TRIPLET2.id, SIMPLE_TRIPLET3.id},
      'nodes': {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id, SIMPLE_TRIPLET2.end_node.id}}],
    # 3.2 hyper (object with thesis)
    [[SIMPLE_TRIPLET1, THESIS_TRIPLET1, THESIS_TRIPLET2], {'triplets': 3, 'nodes': 3},
     {'triplets': {SIMPLE_TRIPLET1.id, THESIS_TRIPLET1.id, THESIS_TRIPLET2.id},
      'nodes': {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id, THESIS_TRIPLET1.end_node.id}}],
    # 3.3 episodic (object with episodic)
    [[SIMPLE_TRIPLET1, EPISODIC_TRIPLET1, EPISODIC_TRIPLET2], {'triplets': 3, 'nodes': 3},
     {'triplets': {SIMPLE_TRIPLET1.id, EPISODIC_TRIPLET1.id, EPISODIC_TRIPLET2.id},
      'nodes': {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id, EPISODIC_TRIPLET1.end_node.id}}],
    # 3.4 episodic (thesis with episodic)
    [[EPISODIC_TRIPLET3, THESIS_TRIPLET3,EPISODIC_TRIPLET4],  {'triplets': 3, 'nodes': 3},
     {'triplets': {EPISODIC_TRIPLET3.id, THESIS_TRIPLET3.id, EPISODIC_TRIPLET4.id},
      'nodes': {EPISODIC_TRIPLET3.start_node.id, EPISODIC_TRIPLET3.end_node.id, THESIS_TRIPLET3.end_node.id}}],
    # 4. добавление связанных триплетов (full, wo_en)
    # 4.1 object -[simple]> object
    [[SIMPLE_TRIPLET2, SIMPLE_TRIPLET1], {'triplets': 2, 'nodes': 3},
     {'triplets': {SIMPLE_TRIPLET2.id, SIMPLE_TRIPLET1.id},
      'nodes': {SIMPLE_TRIPLET2.start_node.id, SIMPLE_TRIPLET2.end_node.id, SIMPLE_TRIPLET1.start_node.id}}],
    # 4.2 object -[hyper]> thesis
    [[THESIS_TRIPLET2, THESIS_TRIPLET1], {'triplets': 2, 'nodes': 3},
     {'triplets': {THESIS_TRIPLET2.id, THESIS_TRIPLET1.id},
      'nodes': {THESIS_TRIPLET2.start_node.id, THESIS_TRIPLET2.end_node.id, THESIS_TRIPLET1.start_node.id}}],
    # 4.3 object -[episodic]> episodic
    [[EPISODIC_TRIPLET2, EPISODIC_TRIPLET1], {'triplets': 2, 'nodes': 3},
     {'triplets': {EPISODIC_TRIPLET2.id, EPISODIC_TRIPLET1.id},
      'nodes': {EPISODIC_TRIPLET2.start_node.id, EPISODIC_TRIPLET2.end_node.id, EPISODIC_TRIPLET1.start_node.id}}],
    # 4.4 thesis -[episodic]> episodic
    [[EPISODIC_TRIPLET3, EPISODIC_TRIPLET4], {'triplets': 2, 'nodes': 3},
     {'triplets': {EPISODIC_TRIPLET3.id, EPISODIC_TRIPLET4.id},
      'nodes': {EPISODIC_TRIPLET3.start_node.id, EPISODIC_TRIPLET3.end_node.id, EPISODIC_TRIPLET4.start_node.id}}],
    # 5. добавление связанных триплетов (full, wo_sn)
    # 5.1 object <[simple]- object
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET2], {'triplets': 2, 'nodes': 3},
     {'triplets': {SIMPLE_TRIPLET1.id, SIMPLE_TRIPLET2.id},
      'nodes': {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id, SIMPLE_TRIPLET2.end_node.id}}],
    # 5.2 thesis <[hyper]- object
    [[SIMPLE_TRIPLET1, THESIS_TRIPLET1], {'triplets': 2, 'nodes': 3},
     {'triplets': {SIMPLE_TRIPLET1.id, THESIS_TRIPLET1.id},
      'nodes': {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id, THESIS_TRIPLET1.end_node.id}}],
    # 5.3 episodic <[episodic]- object
    [[SIMPLE_TRIPLET1, EPISODIC_TRIPLET1], {'triplets': 2, 'nodes': 3},
     {'triplets': {SIMPLE_TRIPLET1.id, EPISODIC_TRIPLET1.id},
      'nodes': {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id, EPISODIC_TRIPLET1.end_node.id}}],
    # 5.4 episodic <[episodic]- thesis
    [[THESIS_TRIPLET3, EPISODIC_TRIPLET4], {'triplets': 2, 'nodes': 3},
     {'triplets': {THESIS_TRIPLET3.id, EPISODIC_TRIPLET4.id},
      'nodes': {THESIS_TRIPLET3.start_node.id, THESIS_TRIPLET3.end_node.id, EPISODIC_TRIPLET4.end_node.id}}],
    # 6. добавление несколько разных триплетов
    # 6.1 simple and simple
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET4], { 'triplets': 2, 'nodes': 4},
     {'triplets': {SIMPLE_TRIPLET1.id, SIMPLE_TRIPLET4.id},
      'nodes': {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id, SIMPLE_TRIPLET4.start_node.id, SIMPLE_TRIPLET4.end_node.id}}],
    # 6.2 simple and hyper
    [[SIMPLE_TRIPLET1, THESIS_TRIPLET3], { 'triplets': 2, 'nodes': 4},
     {'triplets': {SIMPLE_TRIPLET1.id, THESIS_TRIPLET3.id},
      'nodes': {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id, THESIS_TRIPLET3.start_node.id, THESIS_TRIPLET3.end_node.id}}],
    # 6.3 hyper and episodic
    [[THESIS_TRIPLET1, EPISODIC_TRIPLET2], { 'triplets': 2, 'nodes': 4},
     {'triplets': {THESIS_TRIPLET1.id, EPISODIC_TRIPLET2.id},
      'nodes': {THESIS_TRIPLET1.start_node.id, THESIS_TRIPLET1.end_node.id, EPISODIC_TRIPLET2.start_node.id, EPISODIC_TRIPLET2.end_node.id}}],
    # 6.4 simple and episodic
    [[SIMPLE_TRIPLET4, EPISODIC_TRIPLET1], { 'triplets': 2, 'nodes': 4},
     {'triplets': {SIMPLE_TRIPLET4.id, EPISODIC_TRIPLET1.id},
      'nodes': {SIMPLE_TRIPLET4.start_node.id, SIMPLE_TRIPLET4.end_node.id, EPISODIC_TRIPLET1.start_node.id, EPISODIC_TRIPLET1.end_node.id}}],
    # 7. добавление триплетов с одинаковыми строковыми представлениями
    # 7.1 simple
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET1], {'triplets': 1, 'nodes': 2},
     {'triplets': {SIMPLE_TRIPLET1.id},
      'nodes': {SIMPLE_TRIPLET1.start_node.id, SIMPLE_TRIPLET1.end_node.id}}],
    # 7.2 thesis
    [[THESIS_TRIPLET1, THESIS_TRIPLET2], {'triplets': 2, 'nodes': 3},
     {'triplets': {THESIS_TRIPLET1.id, THESIS_TRIPLET2.id},
      'nodes': {THESIS_TRIPLET1.start_node.id, THESIS_TRIPLET1.end_node.id, THESIS_TRIPLET2.start_node.id}}],
    # 7.3 episodic
    [[EPISODIC_TRIPLET1, EPISODIC_TRIPLET2], {'triplets': 2, 'nodes': 3},
     {'triplets': {EPISODIC_TRIPLET1.id, EPISODIC_TRIPLET2.id},
      'nodes': {EPISODIC_TRIPLET1.start_node.id, EPISODIC_TRIPLET1.end_node.id, EPISODIC_TRIPLET2.start_node.id}}]
]

GM_POPULATED_CREATE_TEST_CASES = []
for db_vendor in AVAILABLE_GRAPH_MODELS:
    for i in range(len(GM_CREATE_TEST_CASES)):
        GM_POPULATED_CREATE_TEST_CASES.append(GM_CREATE_TEST_CASES[i] + [db_vendor])

print("Количество порождённых тестов для GM_CREATE:", len(GM_POPULATED_CREATE_TEST_CASES))

###############################################################################################

# init_triplets, expected_create_info, expected_init_count, triplets_to_delete, expected_delete_ginfo, expected_final_count
GM_DELETE_TEST_CASES = [
    # 1. Удаление всего триплета
    # 1.1. Все объекты присутствуют
    # 1.2. Присутвтует только связь
    # 1.3. Присутствует только связи + начальная вершина
    # 1.4. Присутствует только связи + конеченая вершина
    # 2. Удаление связи и стартовой вершины
    # 2.1. Все объекты присутствуют
    # 2.2. Присутствует только связь
    # 3. Удаление связи и конеченой вершины
    # 3.1. Все объекты присутствутю
    # 3.2. Присутствует только связь
    # 4. Удаление только связи
    # 5. Удаление смешанного набора
    # 5.1 Удаление всего триплета + связи и стартовой вершины + связи и конеченой вершины
]

GM_POPULATED_DELETE_TEST_CASES = []
for db_vendor in AVAILABLE_GRAPH_MODELS:
    for i in range(len(GM_DELETE_TEST_CASES)):
        GM_POPULATED_DELETE_TEST_CASES.append(GM_DELETE_TEST_CASES[i] + [db_vendor])

print("Количество порождённых тестов для GM_DELETE:", len(GM_POPULATED_DELETE_TEST_CASES))

###############################################################################################

# triplets, expected_count, expected_graph_cinfo, expected_vector_cinfo
KG_CREATE_TEST_CASES = [
    # два разные триплета
    # у двух трипелтов смежная вершина
    # у двх триплетов одинаковые вершины, но разная связь
    # два одинаковых триплета
]

KG_POPULATED_CREATE_TEST_CASES = []
for vector_vendor in AVAILABLE_EMBEDDING_MODELS:
    for graph_vendor in AVAILABLE_GRAPH_MODELS:
        for i in range(len(KG_CREATE_TEST_CASES)):
            KG_POPULATED_CREATE_TEST_CASES.append(KG_CREATE_TEST_CASES[i] + [f"{vector_vendor}/{graph_vendor}"])

print("Количество порождённых тестов для KG_CREATE:", len(KG_POPULATED_CREATE_TEST_CASES))

# Note: Для разных трипелтов может быть одно векторное представление (нужно это проверять при удалении)

# init_triplets, expected_init_count, delete_triplets, expected_graph_ids, expected_vector_ids
KG_DELETE_TEST_CASES = [
    # удаление всего триплета
    # удаление только связи
    # удаление связи и стартовой вершины
    # удаление связи и конеченой вершины
]

KG_POPULATED_DELETE_TEST_CASES = []
for vector_vendor in AVAILABLE_EMBEDDING_MODELS:
    for graph_vendor in AVAILABLE_GRAPH_MODELS:
        for i in range(len(KG_DELETE_TEST_CASES)):
            KG_POPULATED_DELETE_TEST_CASES.append(KG_DELETE_TEST_CASES[i] + [f"{vector_vendor}/{graph_vendor}"])

print("Количество порождённых тестов для KG_DELETE:", len(KG_POPULATED_DELETE_TEST_CASES))

KG_CLEAR_TEST_CASES = [
    # TODO
]

KG_POPULATED_CLEAR_TEST_CASES = []
for vector_vendor in AVAILABLE_EMBEDDING_MODELS:
    for graph_vendor in AVAILABLE_GRAPH_MODELS:
        for i in range(len(KG_CLEAR_TEST_CASES)):
            KG_POPULATED_CLEAR_TEST_CASES.append(KG_DELETE_TEST_CASES[i] + [f"{vector_vendor}/{graph_vendor}"])
