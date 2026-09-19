import sys
from copy import deepcopy
sys.path.insert(0, "../")

from src.utils.data_structs import Triplet, Node, Relation, NodeType, RelationType

# TO CHANGE
# 'inmemory_kv', 'redis', 'mongo', 'mixed_kv'
AVAILABLE_KV_DBS = ['inmemory_kv', 'redis', 'mongo', 'mixed_kv']

###############################################################################################

SIMPLE_TRIPLET1 = Triplet(
    id='tid_1',
    start_node=Node(id='snid_1', type=NodeType.object, name=None),
    relation=Relation(id='relid_1', type=RelationType.simple, name=None),
    end_node=Node(id='enid_1', type=NodeType.object, name=None)
)
SIMPLE_TRIPLET2 = Triplet(
    id='tid_2',
    start_node=Node(id='snid_2', type=NodeType.object, name=None),
    relation=Relation(id='relid_2', type=RelationType.simple, name=None),
    end_node=Node(id='enid_2', type=NodeType.object, name=None)
)

HYPER_TRIPLET1 = Triplet(
    id='tid_3',
    start_node=Node(id='snid_3', type=NodeType.object, name=None),
    relation=Relation(id='relid_3', type=RelationType.hyper, name=None),
    end_node=Node(id='enid_3', type=NodeType.hyper, name=None)
)
HYPER_TRIPLET2 = Triplet(
    id='tid_4',
    start_node=Node(id='snid_4', type=NodeType.object, name=None),
    relation=Relation(id='relid_4', type=RelationType.hyper, name=None),
    end_node=Node(id='enid_4', type=NodeType.hyper, name=None)
)

EPISODIC_TRIPLET1 = Triplet(
    id='tid_5',
    start_node=Node(id='snid_5', type=NodeType.object, name=None),
    relation=Relation(id='relid_5', type=RelationType.episodic, name=None),
    end_node=Node(id='enid_5', type=NodeType.episodic, name=None)
)
EPISODIC_TRIPLET2 = Triplet(
    id='tid_6',
    start_node=Node(id='snid_6', type=NodeType.hyper, name=None),
    relation=Relation(id='relid_6', type=RelationType.episodic, name=None),
    end_node=Node(id='enid_6', type=NodeType.episodic, name=None)
)

BAD_SAVE_INFO1 = [['456', [SIMPLE_TRIPLET2, HYPER_TRIPLET2]], [123, [SIMPLE_TRIPLET1, HYPER_TRIPLET1]]]
BAD_SAVE_INFO2 = [['456', [SIMPLE_TRIPLET2, HYPER_TRIPLET2]], [True, [SIMPLE_TRIPLET1, HYPER_TRIPLET1]]]
BAD_SAVE_INFO3 = [['456', [SIMPLE_TRIPLET2, HYPER_TRIPLET2]], [None, [SIMPLE_TRIPLET1, HYPER_TRIPLET1]]]

BAD_SAVE_INFO4 = [['456', [SIMPLE_TRIPLET2, HYPER_TRIPLET2]], ['123', f"{[SIMPLE_TRIPLET1, HYPER_TRIPLET1]}"]]
BAD_SAVE_INFO5 = [['456', [SIMPLE_TRIPLET2, HYPER_TRIPLET2]], ['123', [f"{SIMPLE_TRIPLET1}", f"{HYPER_TRIPLET1}"]]]

BAD_SAVE_INFO6 = [['456', [SIMPLE_TRIPLET2, HYPER_TRIPLET2]], ['456', [SIMPLE_TRIPLET1, HYPER_TRIPLET1]]]

SAVE_INFO1 = [['123', []], ['456', [EPISODIC_TRIPLET1, HYPER_TRIPLET2]]]
SAVE_INFO2 = [['456', [EPISODIC_TRIPLET1, HYPER_TRIPLET2]]]
SAVE_INFO3 = [['123', [EPISODIC_TRIPLET2, SIMPLE_TRIPLET2]], ['456', [EPISODIC_TRIPLET1, HYPER_TRIPLET2]]]
SAVE_INFO4 = [['456', [EPISODIC_TRIPLET1]]]

###############################################################################################

# save_info, text_id, expected_triplets, exception, personalai_idsstore
STORE_SAVE_TEST_CASES = [
    # 1. неверный тип у text_id
    # 1.1. число
    [BAD_SAVE_INFO1, None, None, True],
    # 1.2. булевое значение
    [BAD_SAVE_INFO2, None, None, True],
    # 1.3. None
    [BAD_SAVE_INFO3, None, None, True],
    # 2. неверный тип у triplets
    # 2.1. строка
    [BAD_SAVE_INFO4, None, None, True],
    # 2.2. список из строк
    [BAD_SAVE_INFO5, None, None, True],
    # 3. такой text_id уже существует
    [BAD_SAVE_INFO6, None, None, True],
    # 4. пустой triplets
    [SAVE_INFO1, '123', [], False],
    # 5. позитивный тест
    # 5.1. сохранение одного триплета
    [SAVE_INFO2, '456', SAVE_INFO2[0][1], False],
    # 5.2. сохранение нескольких триплетов
    [SAVE_INFO3, '123', SAVE_INFO3[0][1], False]
]

STORE_POPULATED_SAVE_TEST_CASES = []
for db_vendor in AVAILABLE_KV_DBS:
    for i in range(len(STORE_SAVE_TEST_CASES)):
        STORE_POPULATED_SAVE_TEST_CASES.append(
            STORE_SAVE_TEST_CASES[i] + [db_vendor])

###############################################################################################

# save_info, text_id, expected_triplets, exception, personalai_idsstore
STORE_LOAD_TEST_CASES = [
    # 1. неверный тип у text_id
    # 1.1. число
    [SAVE_INFO3, 123, None, True],
    # 1.2. булевое значение
    [SAVE_INFO3, False, None, True],
    # 1.3. None
    [SAVE_INFO3, 123, None, True],
    # 2. такого text_id не существует
    [SAVE_INFO3, '789', None, True],
    # 3. получение пустого списка триплетов
    [SAVE_INFO1, '123', [], False],
    # 4. позитивный тест
    # 4.1. получение одного триплета
    [SAVE_INFO4, '456', SAVE_INFO4[0][1], False],
    # 4.2. получение нескольких триплетов
    [SAVE_INFO3, '123', SAVE_INFO3[0][1], False]
]

STORE_POPULATED_LOAD_TEST_CASES = []
for db_vendor in AVAILABLE_KV_DBS:
    for i in range(len(STORE_LOAD_TEST_CASES)):
        STORE_POPULATED_LOAD_TEST_CASES.append(
            STORE_LOAD_TEST_CASES[i] + [db_vendor])
