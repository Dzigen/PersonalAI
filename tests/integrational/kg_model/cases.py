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
EM_CREATE_TEST_CASES = [
    # 1. пустой список
    [[], False, {'triplets_count': 0, 'nodes_count': 0}],
    # 2. добавление одного триплета
    # 2.1 simple
    [[SIMPLE_TRIPLET1], True, {'triplets_count': 1, 'nodes_count': 2}],
    # 2.2 thesis
    [[THESIS_TRIPLET2], True, {'triplets_count': 1, 'nodes_count': 2}],
    # 2.3 episodic with object
    [[EPISODIC_TRIPLET1], True, {'triplets_count': 1, 'nodes_count': 2}],
    # 2.4 episodic with thesis
    [[EPISODIC_TRIPLET4], True, {'triplets_count': 1, 'nodes_count': 2}],
    # 3. добавление связанных триплетов (full, wo_sn, only_rel)
    # 3.1 simple rel
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET2, SIMPLE_TRIPLET3], True, {'triplets_count': 3, 'nodes_count': 3}],
    # 3.2 hyper (object with thesis)
    [[SIMPLE_TRIPLET1, THESIS_TRIPLET1, THESIS_TRIPLET2], True, {'triplets_count': 2, 'nodes_count': 3}],
    # 3.3 episodic (object with episodic)
    [[SIMPLE_TRIPLET1, EPISODIC_TRIPLET1, EPISODIC_TRIPLET2], True, {'triplets_count': 2, 'nodes_count': 3}],
    # 3.4 episodic (thesis with episodic)
    [[EPISODIC_TRIPLET3, THESIS_TRIPLET3,EPISODIC_TRIPLET4], True, {'triplets_count': 2, 'nodes_count': 3}],
    # 4. добавление связанных триплетов (full, wo_en)
    # 4.1 object -[simple]> object
    [[SIMPLE_TRIPLET2, SIMPLE_TRIPLET1], True, {'triplets_count': 2, 'nodes_count': 3}],
    # 4.2 object -[hyper]> thesis
    [[THESIS_TRIPLET2, THESIS_TRIPLET1], True, {'triplets_count': 1, 'nodes_count': 3}],
    # 4.3 object -[episodic]> episodic
    [[EPISODIC_TRIPLET2, EPISODIC_TRIPLET1], True, {'triplets_count': 1, 'nodes_count': 3}],
    # 4.4 thesis -[episodic]> episodic
    [[EPISODIC_TRIPLET3, EPISODIC_TRIPLET4], True, {'triplets_count': 1, 'nodes_count': 3}],
    # 5. добавление связанных триплетов (full, wo_sn)
    # 5.1 object <[simple]- object
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET2], True, {'triplets_count': 2, 'nodes_count': 3}],
    # 5.2 thesis <[hyper]- object
    [[SIMPLE_TRIPLET1, THESIS_TRIPLET1], True, {'triplets_count': 2, 'nodes_count': 3}],
    # 5.3 episodic <[episodic]- object
    [[SIMPLE_TRIPLET1, EPISODIC_TRIPLET1], True, {'triplets_count': 2, 'nodes_count': 3}],
    # 5.4 episodic <[episodic]- thesis
    [[THESIS_TRIPLET3, EPISODIC_TRIPLET4], True, {'triplets_count': 2, 'nodes_count': 3}],
    # 6. добавление несколько разных триплетов
    # 6.1 simple and simple
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET4], True, {'triplets_count': 2, 'nodes_count': 4}],
    # 6.2 simple and hyper
    [[SIMPLE_TRIPLET1, THESIS_TRIPLET3], True, {'triplets_count': 2, 'nodes_count': 4}],
    # 6.3 hyper and episodic
    [[THESIS_TRIPLET1, EPISODIC_TRIPLET2], True, {'triplets_count': 2, 'nodes_count': 4}],
    # 6.4 simple and episodic
    [[SIMPLE_TRIPLET4, EPISODIC_TRIPLET1], True, {'triplets_count': 2, 'nodes_count': 4}],
    # 7. добавление триплетов с одинаковыми строковыми представлениями
    # 7.1 simple
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET1], True, {'triplets_count': 1, 'nodes_count': 2}],
    # 7.2 thesis
    [[THESIS_TRIPLET1, THESIS_TRIPLET2], True, {'triplets_count': 1, 'nodes_count': 3}],
    # 7.3 episodic
    [[EPISODIC_TRIPLET1, EPISODIC_TRIPLET2], True, {'triplets_count': 1, 'nodes_count': 3}]
]

EM_POPULATED_CREATE_TEST_CASES = []
for db_vendor in AVAILABLE_EMBEDDING_MODELS:
    for i in range(len(EM_CREATE_TEST_CASES)):
        EM_POPULATED_CREATE_TEST_CASES.append(EM_CREATE_TEST_CASES[i] + [db_vendor])

print("Количество порождённых тестов для EM_CREATE:", len(EM_POPULATED_CREATE_TEST_CASES))

###############################################################################################

EM_DELETE_TEST_CASES = [
    # TODO
]

EM_POPULATED_DELETE_TEST_CASES = []
for db_vendor in AVAILABLE_EMBEDDING_MODELS:
    for i in range(len(EM_DELETE_TEST_CASES)):
        EM_POPULATED_DELETE_TEST_CASES.append(EM_DELETE_TEST_CASES[i] + [db_vendor])

print("Количество порождённых тестов для EM_DELETE:", len(EM_POPULATED_DELETE_TEST_CASES))

###############################################################################################

# graph-model tests
GM_CREATE_TEST_CASES = [
    # 1. пустой список
    [[], {'triplets_count': 0, 'nodes_count': 0}],
    # 2. добавление одного триплета
    # 2.1 simple
    [[SIMPLE_TRIPLET1], {'triplets_count': 1, 'nodes_count': 2}],
    # 2.2 thesis
    [[THESIS_TRIPLET2], {'triplets_count': 1, 'nodes_count': 2}],
    # 2.3 episodic with object
    [[EPISODIC_TRIPLET1], {'triplets_count': 1, 'nodes_count': 2}],
    # 2.4 episodic with thesis
    [[EPISODIC_TRIPLET4], {'triplets_count': 1, 'nodes_count': 2}],
    # 3. добавление связанных триплетов (full, wo_sn, only_rel)
    # 3.1 simple rel
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET2, SIMPLE_TRIPLET3], {'triplets_count': 3, 'nodes_count': 3}],
    # 3.2 hyper (object with thesis)
    [[SIMPLE_TRIPLET1, THESIS_TRIPLET1, THESIS_TRIPLET2], {'triplets_count': 3, 'nodes_count': 3}],
    # 3.3 episodic (object with episodic)
    [[SIMPLE_TRIPLET1, EPISODIC_TRIPLET1, EPISODIC_TRIPLET2], {'triplets_count': 3, 'nodes_count': 3}],
    # 3.4 episodic (thesis with episodic)
    [[EPISODIC_TRIPLET3, THESIS_TRIPLET3,EPISODIC_TRIPLET4],  {'triplets_count': 3, 'nodes_count': 3}],
    # 4. добавление связанных триплетов (full, wo_en)
    # 4.1 object -[simple]> object
    [[SIMPLE_TRIPLET2, SIMPLE_TRIPLET1], {'triplets_count': 2, 'nodes_count': 3}],
    # 4.2 object -[hyper]> thesis
    [[THESIS_TRIPLET2, THESIS_TRIPLET1], {'triplets_count': 2, 'nodes_count': 3}],
    # 4.3 object -[episodic]> episodic
    [[EPISODIC_TRIPLET2, EPISODIC_TRIPLET1], {'triplets_count': 2, 'nodes_count': 3}],
    # 4.4 thesis -[episodic]> episodic
    [[EPISODIC_TRIPLET3, EPISODIC_TRIPLET4], {'triplets_count': 2, 'nodes_count': 3}],
    # 5. добавление связанных триплетов (full, wo_sn)
    # 5.1 object <[simple]- object
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET2], {'triplets_count': 2, 'nodes_count': 3}],
    # 5.2 thesis <[hyper]- object
    [[SIMPLE_TRIPLET1, THESIS_TRIPLET1], {'triplets_count': 2, 'nodes_count': 3}],
    # 5.3 episodic <[episodic]- object
    [[SIMPLE_TRIPLET1, EPISODIC_TRIPLET1], {'triplets_count': 2, 'nodes_count': 3}],
    # 5.4 episodic <[episodic]- thesis
    [[THESIS_TRIPLET3, EPISODIC_TRIPLET4], {'triplets_count': 2, 'nodes_count': 3}],
    # 6. добавление несколько разных триплетов
    # 6.1 simple and simple
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET4], { 'triplets_count': 2, 'nodes_count': 4}],
    # 6.2 simple and hyper
    [[SIMPLE_TRIPLET1, THESIS_TRIPLET3], { 'triplets_count': 2, 'nodes_count': 4}],
    # 6.3 hyper and episodic
    [[THESIS_TRIPLET1, EPISODIC_TRIPLET2], { 'triplets_count': 2, 'nodes_count': 4}],
    # 6.4 simple and episodic
    [[SIMPLE_TRIPLET4, EPISODIC_TRIPLET1], { 'triplets_count': 2, 'nodes_count': 4}],
    # 7. добавление триплетов с одинаковыми строковыми представлениями
    # 7.1 simple
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET1], {'triplets_count': 1, 'nodes_count': 2}],
    # 7.2 thesis
    [[THESIS_TRIPLET1, THESIS_TRIPLET2], {'triplets_count': 2, 'nodes_count': 3}],
    # 7.3 episodic
    [[EPISODIC_TRIPLET1, EPISODIC_TRIPLET2], {'triplets_count': 2, 'nodes_count': 3}]
]

GM_POPULATED_CREATE_TEST_CASES = []
for db_vendor in AVAILABLE_GRAPH_MODELS:
    for i in range(len(GM_CREATE_TEST_CASES)):
        GM_POPULATED_CREATE_TEST_CASES.append(GM_CREATE_TEST_CASES[i] + [db_vendor])

print("Количество порождённых тестов для GM_CREATE:", len(GM_POPULATED_CREATE_TEST_CASES))

###############################################################################################

GM_DELETE_TEST_CASES = [
    # TODO
]

GM_POPULATED_DELETE_TEST_CASES = []
for db_vendor in AVAILABLE_GRAPH_MODELS:
    for i in range(len(GM_DELETE_TEST_CASES)):
        GM_POPULATED_DELETE_TEST_CASES.append(GM_DELETE_TEST_CASES[i] + [db_vendor])

print("Количество порождённых тестов для GM_DELETE:", len(GM_POPULATED_DELETE_TEST_CASES))

###############################################################################################
