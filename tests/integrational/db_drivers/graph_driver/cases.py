import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.utils.data_structs import Triplet, NodeCreator, Relation, RelationType, NodeType, TripletCreator
from src.utils.errors import ReturnInfo

# TO CHANGE
AVAILABLE_GRAPH_DBS = ['kuzu', 'neo4j', 'inmemory_graph']

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

# creation info
FULL_CREATION_INFO = {'s_node': True, 'rel': True, 'e_node': True}
WO_SN_CREATION_INFO = {'s_node': False, 'rel': True, 'e_node': True}
WO_EN_CREATION_INFO = {'s_node': True, 'rel': True, 'e_node': False}
ONLY_REL_CREATION_INFO = {'s_node': False, 'rel': True, 'e_node': False}

ALL_N_TYPES = [NodeType.object, NodeType.hyper, NodeType.episodic]

###############################################################################################

GRAPHDB_CREATE_TEST_CASES = [
    # 1. пустой список
    [[[]], [{}], {'exception': False, 'triplets_count': 0, 'nodes_count': 0}],
    # 2. добавление одного триплета (полностью с creation_info None)
    # 2.1 simple
    [[[SIMPLE_TRIPLET1]], [{}], {'exception': False, 'triplets_count': 1, 'nodes_count': 2}],
    # 2.2 thesis
    [[[THESIS_TRIPLET2]], [{}], {'exception': False, 'triplets_count': 1, 'nodes_count': 2}],
    # 2.3 episodic with object
    [[[EPISODIC_TRIPLET1]], [{}], {'exception': False, 'triplets_count': 1, 'nodes_count': 2}],
    # 2.4 episodic with thesis
    [[[EPISODIC_TRIPLET4]], [{}], {'exception': False, 'triplets_count': 1, 'nodes_count': 2}],
    # 3. добавление одного триплета (полностью с creation_info не None)
    # 3.1 simple
    [[[SIMPLE_TRIPLET1]], [{0:FULL_CREATION_INFO}], {'exception': False, 'triplets_count': 1, 'nodes_count': 2}],
    # 3.2 thesis
    [[[THESIS_TRIPLET2]], [{0:FULL_CREATION_INFO}], {'exception': False, 'triplets_count': 1, 'nodes_count': 2}],
    # 3.3 episodic with object
    [[[EPISODIC_TRIPLET1]], [{0:FULL_CREATION_INFO}], {'exception': False, 'triplets_count': 1, 'nodes_count': 2}],
    # 3.4 episodic with thesis
    [[[EPISODIC_TRIPLET4]], [{0:FULL_CREATION_INFO}], {'exception': False, 'triplets_count': 1, 'nodes_count': 2}],
    # 4. добалвение одного триплета (только связь c заданным creation_info)
    # 4.1 simple rel
    [[[SIMPLE_TRIPLET1, SIMPLE_TRIPLET2],[SIMPLE_TRIPLET3]], [{0:FULL_CREATION_INFO, 1:WO_SN_CREATION_INFO}, {0:ONLY_REL_CREATION_INFO}], {'exception': False, 'triplets_count': 3, 'nodes_count': 3}],
    # 4.2 hyper (object with thesis)
    [[[SIMPLE_TRIPLET2, THESIS_TRIPLET1],[THESIS_TRIPLET2]], [{0:FULL_CREATION_INFO, 1:FULL_CREATION_INFO}, {0:ONLY_REL_CREATION_INFO}], {'exception': False, 'triplets_count': 3, 'nodes_count': 4}],
    # 4.3 episodic (object with episodic)
    [[[SIMPLE_TRIPLET1, EPISODIC_TRIPLET1],[EPISODIC_TRIPLET2]], [{0:FULL_CREATION_INFO, 1:WO_SN_CREATION_INFO}, {0:ONLY_REL_CREATION_INFO}], {'exception': False, 'triplets_count': 3, 'nodes_count': 3}],
    # 4.4 episodic (thesis with episodic)
    [[[EPISODIC_TRIPLET3, THESIS_TRIPLET3],[EPISODIC_TRIPLET4]], [{0:FULL_CREATION_INFO, 1:WO_SN_CREATION_INFO}, {0:ONLY_REL_CREATION_INFO}], {'exception': False, 'triplets_count': 3, 'nodes_count': 3}],
    # 5. добавление одного триплета (связь и стартовая вершина c заданным creation_info)
    # 5.1 object -[simple]> object
    [[[SIMPLE_TRIPLET2], [SIMPLE_TRIPLET1]], [{0:FULL_CREATION_INFO},{0:WO_EN_CREATION_INFO}], {'exception': False, 'triplets_count': 2, 'nodes_count': 3}],
    # 5.2 object -[hyper]> thesis
    [[[THESIS_TRIPLET2], [THESIS_TRIPLET1]], [{0:FULL_CREATION_INFO},{0:WO_EN_CREATION_INFO}], {'exception': False, 'triplets_count': 2, 'nodes_count': 3}],
    # 5.3 object -[episodic]> episodic
    [[[EPISODIC_TRIPLET2], [EPISODIC_TRIPLET1]], [{0:FULL_CREATION_INFO},{0:WO_EN_CREATION_INFO}], {'exception': False, 'triplets_count': 2, 'nodes_count': 3}],
    # 5.4 thesis -[episodic]> episodic
    [[[EPISODIC_TRIPLET3], [EPISODIC_TRIPLET4]], [{0:FULL_CREATION_INFO},{0:WO_EN_CREATION_INFO}], {'exception': False, 'triplets_count': 2, 'nodes_count': 3}],
    # 6. добавление одного триплета (связь и конечная вершина c заданным creation_info)
    # 6.1 object <[simple]- object
    [[[SIMPLE_TRIPLET1], [SIMPLE_TRIPLET2]], [{0:FULL_CREATION_INFO},{0:WO_SN_CREATION_INFO}], {'exception': False, 'triplets_count': 2, 'nodes_count': 3}],
    # 6.2 thesis <[hyper]- object
    [[[SIMPLE_TRIPLET1], [THESIS_TRIPLET1]], [{0:FULL_CREATION_INFO},{0:WO_SN_CREATION_INFO}], {'exception': False, 'triplets_count': 2, 'nodes_count': 3}],
    # 6.3 episodic <[episodic]- object
    [[[SIMPLE_TRIPLET1], [EPISODIC_TRIPLET1]], [{0:FULL_CREATION_INFO},{0:WO_SN_CREATION_INFO}], {'exception': False, 'triplets_count': 2, 'nodes_count': 3}],
    # 6.4 episodic <[episodic]- thesis
    [[[THESIS_TRIPLET3], [EPISODIC_TRIPLET4]], [{0:FULL_CREATION_INFO},{0:WO_SN_CREATION_INFO}], {'exception': False, 'triplets_count': 2, 'nodes_count': 3}],
    # 7. добавление несколько разных триплетов (полностью c заданным creation_info)
    # 7.1 simple and simple
    [[[SIMPLE_TRIPLET1, SIMPLE_TRIPLET4]], [{0:FULL_CREATION_INFO, 1:FULL_CREATION_INFO}], {'exception': False, 'triplets_count': 2, 'nodes_count': 4}],
    # 7.2 simple and hyper
    [[[SIMPLE_TRIPLET1, THESIS_TRIPLET3]], [{0:FULL_CREATION_INFO, 1:FULL_CREATION_INFO}], {'exception': False, 'triplets_count': 2, 'nodes_count': 4}],
    # 7.3 hyper and episodic
    [[[THESIS_TRIPLET1, EPISODIC_TRIPLET2]], [{0:FULL_CREATION_INFO, 1:FULL_CREATION_INFO}], {'exception': False, 'triplets_count': 2, 'nodes_count': 4}],
    # 7.4 simple and episodic
    [[[SIMPLE_TRIPLET4, EPISODIC_TRIPLET1]], [{0:FULL_CREATION_INFO, 1:FULL_CREATION_INFO}], {'exception': False, 'triplets_count': 2, 'nodes_count': 4}],
    # 8. добавление нескольких связанных триплетов без creation info
    [[[SIMPLE_TRIPLET1, SIMPLE_TRIPLET2]], [{}], {'exception': False, 'triplets_count': 3, 'nodes_count': 4}]
]

GRAPHDB_POPULATED_CREATE_TEST_CASES = []
for db_vendor in AVAILABLE_GRAPH_DBS:
    for i in range(len(GRAPHDB_CREATE_TEST_CASES)):
        GRAPHDB_POPULATED_CREATE_TEST_CASES.append(GRAPHDB_CREATE_TEST_CASES[i] + [db_vendor])

###############################################################################################

GRAPHDB_DELETE_TEST_CASES = [
    # 1. пустой список
    [[SIMPLE_TRIPLET3, SIMPLE_TRIPLET4], {0:FULL_CREATION_INFO, 1:WO_SN_CREATION_INFO}, [], {'exception': False, 'triplets_count': 2, 'nodes_count': 3}],
    # 2. один существующий триплет (удаляется связь и вершины)
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET4], {0:FULL_CREATION_INFO, 1:FULL_CREATION_INFO}, [SIMPLE_TRIPLET1.id], {'exception': False, 'triplets_count': 1, 'nodes_count': 2}],
    # 3. один существующий триплет (удаляется только связь)
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET2, SIMPLE_TRIPLET3], {0:FULL_CREATION_INFO, 1:WO_SN_CREATION_INFO, 2:ONLY_REL_CREATION_INFO}, [SIMPLE_TRIPLET3.id], {'exception': False, 'triplets_count': 2, 'nodes_count': 3}],
    # 4. один несуществующий триплет
    [[SIMPLE_TRIPLET1], {0:FULL_CREATION_INFO}, [SIMPLE_TRIPLET2.id], {'exception': False, 'triplets_count': 1, 'nodes_count': 2}],
    # 5. несколько триплетов (на удаление связи; связи и вершины; связи и вершин)
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET3, THESIS_TRIPLET2, EPISODIC_TRIPLET2], {0:FULL_CREATION_INFO, 1:WO_EN_CREATION_INFO, 2:WO_SN_CREATION_INFO, 3:WO_SN_CREATION_INFO}, [SIMPLE_TRIPLET1.id, THESIS_TRIPLET2.id, EPISODIC_TRIPLET2.id], {'exception': False, 'triplets_count': 1, 'nodes_count': 2}],
    # 6. несколько триплетов (на удаление связи; удаление несуществующего триплета; удаление связи и вершины)
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET3, THESIS_TRIPLET2, EPISODIC_TRIPLET2], {0:FULL_CREATION_INFO, 1:WO_EN_CREATION_INFO, 2:WO_SN_CREATION_INFO, 3:WO_SN_CREATION_INFO}, [SIMPLE_TRIPLET1.id, 'unknow_id', THESIS_TRIPLET2.id], {'exception': False, 'triplets_count': 2, 'nodes_count': 4}],
    # 7. неверный формат идентификатора 1
    [[SIMPLE_TRIPLET1], {0:FULL_CREATION_INFO}, [123], {'exception': True, 'triplets_count': 1, 'nodes_count': 2}],
    # 8. неверный формат идентификатора 2
    [[SIMPLE_TRIPLET1], {0:FULL_CREATION_INFO}, [True], {'exception': True, 'triplets_count': 1, 'nodes_count': 2}],
    # 9. неверный формат идентификатора 3
    [[SIMPLE_TRIPLET1], {0:FULL_CREATION_INFO}, [None], {'exception': True, 'triplets_count': 1, 'nodes_count': 2}]
]

GRAPHDB_POPULATED_DELETE_TEST_CASES = []
for db_vendor in AVAILABLE_GRAPH_DBS:
    for i in range(len(GRAPHDB_DELETE_TEST_CASES)):
        GRAPHDB_POPULATED_DELETE_TEST_CASES.append(GRAPHDB_DELETE_TEST_CASES[i] + [db_vendor])

###############################################################################################

GRAPHDB_READ_TEST_CASES = [
    # 1. пустой список
    [[SIMPLE_TRIPLET1,SIMPLE_TRIPLET2], {0:FULL_CREATION_INFO, 1:WO_SN_CREATION_INFO}, [], {'exception': False, 'output_ids': []}],
    # 2. один существующий триплет
    [[SIMPLE_TRIPLET1,SIMPLE_TRIPLET2], {0:FULL_CREATION_INFO, 1:WO_SN_CREATION_INFO}, [SIMPLE_TRIPLET1.id], {'exception': False, 'output_ids': [SIMPLE_TRIPLET1.id]}],
    # 3. один несуществующий триплет
    [[SIMPLE_TRIPLET1,SIMPLE_TRIPLET2], {0:FULL_CREATION_INFO, 1:WO_SN_CREATION_INFO}, [SIMPLE_TRIPLET3.id], {'exception': False, 'output_ids': []}],
    # 4. несколько существующих триплетов
    [[SIMPLE_TRIPLET1,SIMPLE_TRIPLET2], {0:FULL_CREATION_INFO, 1:WO_SN_CREATION_INFO}, [SIMPLE_TRIPLET1.id, SIMPLE_TRIPLET2.id], {'exception': False, 'output_ids': [SIMPLE_TRIPLET1.id, SIMPLE_TRIPLET2.id]}],
    # 5. в списке есть несуществующий идентификатор триплета
    [[SIMPLE_TRIPLET1,SIMPLE_TRIPLET2], {0:FULL_CREATION_INFO, 1:WO_SN_CREATION_INFO}, [SIMPLE_TRIPLET1.id, SIMPLE_TRIPLET3.id], {'exception': False, 'output_ids': [SIMPLE_TRIPLET1.id]}],
    # 6. неверный формат идентификатора 1
    [[SIMPLE_TRIPLET1,SIMPLE_TRIPLET2], {0:FULL_CREATION_INFO, 1:WO_SN_CREATION_INFO}, [123], {'exception': True, 'output_ids': []}],
    # 7. неверный формат идентификатора 2
    [[SIMPLE_TRIPLET1,SIMPLE_TRIPLET2], {0:FULL_CREATION_INFO, 1:WO_SN_CREATION_INFO}, [True], {'exception': True, 'output_ids': []}],
    # 8. неверный формат идентификатора 3
    [[SIMPLE_TRIPLET1,SIMPLE_TRIPLET2], {0:FULL_CREATION_INFO, 1:WO_SN_CREATION_INFO}, [None], {'exception': True, 'output_ids': []}]
]

GRAPHDB_POPULATED_READ_TEST_CASES = []
for db_vendor in AVAILABLE_GRAPH_DBS:
    for i in range(len(GRAPHDB_READ_TEST_CASES)):
        GRAPHDB_POPULATED_READ_TEST_CASES.append(GRAPHDB_READ_TEST_CASES[i] + [db_vendor])

###############################################################################################

GRAPHDB_COUNT_TEST_CASES = [
    # 1. нуль элементов
    [[], {}, {'triplets_count': 0, 'nodes_count': 0}],
    # 2. один элемент
    [[SIMPLE_TRIPLET1], {}, {'triplets_count': 1, 'nodes_count': 2}],
    # 3. несколько элементов с creation_info = None
    [[SIMPLE_TRIPLET1,SIMPLE_TRIPLET2], {}, {'triplets_count': 3, 'nodes_count': 4}],
    # 4. несколько элементов с меками объектов-дубликатов (creation_info != None)
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET2], {0:FULL_CREATION_INFO, 1:WO_SN_CREATION_INFO}, {'triplets_count': 2, 'nodes_count': 3}]
]

GRAPHDB_POPULATED_COUNT_TEST_CASES = []
for db_vendor in AVAILABLE_GRAPH_DBS:
    for i in range(len(GRAPHDB_COUNT_TEST_CASES)):
        GRAPHDB_POPULATED_COUNT_TEST_CASES.append(GRAPHDB_COUNT_TEST_CASES[i] + [db_vendor])

###############################################################################################

GRAPHDB_EXIST_TEST_CASES = [
    # 1. элемент существует
    [[SIMPLE_TRIPLET1, EPISODIC_TRIPLET3], SIMPLE_TRIPLET1.id, {'exception': False, 'exist': True, 'type': 'triplet'}],
    # 2. элемента не существует
    [[SIMPLE_TRIPLET1, EPISODIC_TRIPLET3], 'unknown_id', {'exception': False, 'exist': False, 'type': 'triplet'}],
    # 3. неверный формат идентификатора # 1
    [[SIMPLE_TRIPLET1, EPISODIC_TRIPLET3], 789, {'exception': True, 'exist': False, 'type': 'triplet'}],
    # 4. неверный формат идентификатора # 2
    [[SIMPLE_TRIPLET1, EPISODIC_TRIPLET3], False, {'exception': True, 'exist': False, 'type': 'triplet'}],
    # 5. неверный формат идентификатора # 3
    [[SIMPLE_TRIPLET1, EPISODIC_TRIPLET3], None, {'exception': True, 'exist': False, 'type': 'triplet'}],
    # 6. Вершина существует
    [[SIMPLE_TRIPLET1, EPISODIC_TRIPLET3], OBJECT_NODE1.id, {'exception': False, 'exist': True, 'type': 'node'}],
    # 7. Вершины не существует
    [[SIMPLE_TRIPLET1, EPISODIC_TRIPLET3], OBJECT_NODE4.id, {'exception': False, 'exist': False, 'type': 'node'}]
]

GRAPHDB_POPULATED_EXIST_TEST_CASES = []
for db_vendor in AVAILABLE_GRAPH_DBS:
    for i in range(len(GRAPHDB_EXIST_TEST_CASES)):
        GRAPHDB_POPULATED_EXIST_TEST_CASES.append(GRAPHDB_EXIST_TEST_CASES[i] + [db_vendor])

###############################################################################################

GRAPHDB_CLEAR_TEST_CASES = [
    # 1. чистка пустой бд
    [[], {'triplets_count': 0, 'nodes_count': 0}],
    # 2. чистка бд с одним триплетом
    # 2.1. simple
    [[SIMPLE_TRIPLET1], {'triplets_count': 1, 'nodes_count': 2}],
    # 2.2. thesis with object
    [[THESIS_TRIPLET1], {'triplets_count': 1, 'nodes_count': 2}],
    # 2.3. episodic with object
    [[EPISODIC_TRIPLET1], {'triplets_count': 1, 'nodes_count': 2}],
    # 2.4. episodic with thesis
    [[EPISODIC_TRIPLET4], {'triplets_count': 1, 'nodes_count': 2}],
    # 3. чиста бд с несколькими элементами
    [[SIMPLE_TRIPLET1, THESIS_TRIPLET1, EPISODIC_TRIPLET1, EPISODIC_TRIPLET4], {'triplets_count': 7, 'nodes_count': 8}]
]

GRAPHDB_POPULATED_CLEAR_TEST_CASES = []
for db_vendor in AVAILABLE_GRAPH_DBS:
    for i in range(len(GRAPHDB_CLEAR_TEST_CASES)):
        GRAPHDB_POPULATED_CLEAR_TEST_CASES.append(GRAPHDB_CLEAR_TEST_CASES[i] + [db_vendor])

###############################################################################################

GRAPHDB_GET_ADJECENT_TEST_CASES = [
    # 1. одна смежная вершина
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET2],{0:FULL_CREATION_INFO, 1:WO_SN_CREATION_INFO}, OBJECT_NODE1.id, ALL_N_TYPES, {'exception': False, 'output_ids': {OBJECT_NODE2.id}}],
    # 2. несколько смежных вершин
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET2],{0:FULL_CREATION_INFO, 1:WO_SN_CREATION_INFO}, OBJECT_NODE2.id, ALL_N_TYPES, {'exception': False, 'output_ids': {OBJECT_NODE1.id, OBJECT_NODE3.id}}],
    # 3. несуществующий идентифкатор
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET2],{0:FULL_CREATION_INFO, 1:WO_SN_CREATION_INFO}, OBJECT_NODE4.id, ALL_N_TYPES, {'exception': False, 'output_ids': set()}],
    # 4. неверный формат идентификатора 1
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET2],{0:FULL_CREATION_INFO, 1:WO_SN_CREATION_INFO}, 123, ALL_N_TYPES, {'exception': True, 'output_ids': set()}],
    # 5. неверный формат идентификатора 2
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET2],{0:FULL_CREATION_INFO, 1:WO_SN_CREATION_INFO}, True, ALL_N_TYPES, {'exception': True, 'output_ids': set()}],
    # 6. неверный формат идентификатора 3
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET2],{0:FULL_CREATION_INFO, 1:WO_SN_CREATION_INFO}, None, ALL_N_TYPES, {'exception': True, 'output_ids': set()}]
]

GRAPHDB_POPULATED_GET_ADJECENT_TEST_CASES = []
for db_vendor in AVAILABLE_GRAPH_DBS:
    for i in range(len(GRAPHDB_GET_ADJECENT_TEST_CASES)):
        GRAPHDB_POPULATED_GET_ADJECENT_TEST_CASES.append(GRAPHDB_GET_ADJECENT_TEST_CASES[i] + [db_vendor])

###############################################################################################

GRAPHDB_GET_TRIPLETS_TEST_CASES = [
    # 1. между нодами нет связей
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET4],{0:FULL_CREATION_INFO, 1:FULL_CREATION_INFO}, (OBJECT_NODE1.id,OBJECT_NODE3.id), {
        'exception': False, 'exist': [True,True], 'output_ids': set(), 'count': 0, 'triplets': 2, 'nodes': 4}],
    # 2.между нодами одна связь
    # 2.1 циклическая связь
    [[SIMPLE_TRIPLET5],{0:WO_EN_CREATION_INFO}, (OBJECT_NODE1.id,OBJECT_NODE1.id), {
        'exception': False, 'exist': [True,True],'output_ids': {SIMPLE_TRIPLET5.id}, 'count': 1, 'triplets': 1, 'nodes': 1}],
    # 2.2 между разными вершинами
    [[SIMPLE_TRIPLET1],{0:FULL_CREATION_INFO}, (OBJECT_NODE1.id,OBJECT_NODE2.id), {
        'exception': False, 'exist': [True,True],'output_ids': {SIMPLE_TRIPLET1.id}, 'count': 1, 'triplets': 1, 'nodes': 2}],
    # 3.между нодами несколько связей
    [[SIMPLE_TRIPLET1, SIMPLE_TRIPLET1_2], {0:FULL_CREATION_INFO, 1:ONLY_REL_CREATION_INFO}, (OBJECT_NODE1.id, OBJECT_NODE2.id), {
        'exception': False, 'exist': [True,True], 'output_ids': {SIMPLE_TRIPLET1.id, SIMPLE_TRIPLET1_2.id}, 'count': 2, 'triplets': 2, 'nodes': 2}],
    # 4.несуществующий идентифкатор
    # 4.1 стартовый
    [[SIMPLE_TRIPLET1],{0:FULL_CREATION_INFO}, ('unkown_id', OBJECT_NODE1.id), {
        'exception': True, 'exist': [False,True], 'output_ids': {}, 'count': 0, 'triplets': 1, 'nodes': 2}],
    # 4.2 конечный
    [[SIMPLE_TRIPLET1],{0:FULL_CREATION_INFO}, (OBJECT_NODE1.id, 'unknown_id'), {
        'exception': True, 'exist': [True,False], 'output_ids': {}, 'count': 0, 'triplets': 1, 'nodes': 2}],
    # 4.3 оба
    [[SIMPLE_TRIPLET1],{0:FULL_CREATION_INFO}, ('unknown_id', 'unknown_id'), {
        'exception': True, 'exist': [False, False], 'output_ids': {}, 'count': 0, 'triplets': 1, 'nodes': 2}],
    # 5.неверный формат идентификатора 1
    [[SIMPLE_TRIPLET1],{0:FULL_CREATION_INFO}, (OBJECT_NODE1.id, 123), {
        'exception': True, 'exist': [True,None], 'output_ids': {}, 'count': 0, 'triplets': 1, 'nodes': 2}],
    # 6.неверный формат идентификатора 2
    [[SIMPLE_TRIPLET1],{0:FULL_CREATION_INFO}, (OBJECT_NODE1.id, True), {
        'exception': True, 'exist': [True,None], 'output_ids': {}, 'count': 0, 'triplets': 1, 'nodes': 2}],
    # 7.неверный формат идентификатора 3
    [[SIMPLE_TRIPLET1],{0:FULL_CREATION_INFO}, (OBJECT_NODE1.id, None), {
        'exception': True, 'exist': [True,None], 'output_ids': {}, 'count': 0, 'triplets': 1, 'nodes': 2}]
]

GRAPHDB_POPULATED_GET_TRIPLETS_TEST_CASES = []
for db_vendor in AVAILABLE_GRAPH_DBS:
    for i in range(len(GRAPHDB_GET_TRIPLETS_TEST_CASES)):
        GRAPHDB_POPULATED_GET_TRIPLETS_TEST_CASES.append(GRAPHDB_GET_TRIPLETS_TEST_CASES[i] + [db_vendor])
