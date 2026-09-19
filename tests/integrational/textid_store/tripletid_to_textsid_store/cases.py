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

SAVE_INFO1 = [['123', []], ['456', [EPISODIC_TRIPLET1, HYPER_TRIPLET2]]]
SAVE_INFO2 = [['123', [SIMPLE_TRIPLET1, SIMPLE_TRIPLET2]], ['123', [SIMPLE_TRIPLET1]]]
SAVE_INFO3 = [['123', [SIMPLE_TRIPLET1, SIMPLE_TRIPLET2]], ['456', [SIMPLE_TRIPLET1]]]
SAVE_INFO4 = [['123', [SIMPLE_TRIPLET1, SIMPLE_TRIPLET2]], ['456', [SIMPLE_TRIPLET1, SIMPLE_TRIPLET2]]]
SAVE_INFO5 = [['123', [SIMPLE_TRIPLET1, SIMPLE_TRIPLET2, HYPER_TRIPLET1]], ['456', [SIMPLE_TRIPLET1, SIMPLE_TRIPLET2, HYPER_TRIPLET1]]]
SAVE_INFO6 = [['123', [SIMPLE_TRIPLET1]],['456', [SIMPLE_TRIPLET2]]]

SAVE_INFO7 = [['123', [SIMPLE_TRIPLET1]], ['456', [SIMPLE_TRIPLET1]], ['789', [SIMPLE_TRIPLET1]]]
SAVE_INFO8 = [['123', [SIMPLE_TRIPLET1, SIMPLE_TRIPLET2]], ['456', [SIMPLE_TRIPLET1, SIMPLE_TRIPLET2]], ['789', [SIMPLE_TRIPLET1, SIMPLE_TRIPLET2]]]
SAVE_INFO9 = [['123', [SIMPLE_TRIPLET1, SIMPLE_TRIPLET2, HYPER_TRIPLET1]], ['456', [SIMPLE_TRIPLET1, SIMPLE_TRIPLET2, HYPER_TRIPLET1]], ['789', [SIMPLE_TRIPLET1, SIMPLE_TRIPLET2, HYPER_TRIPLET1]]]
SAVE_INFO10 = [['123', [SIMPLE_TRIPLET1]], ['456', [SIMPLE_TRIPLET2]], ['789', [HYPER_TRIPLET2]]]

###############################################################################################

# save_info, expected_triplettotexts_map, exception, textidstore_instance
STORE_SAVE_TEST_CASES = [
    # 1. неверный тип у text_id
    # 1.1. число
    [BAD_SAVE_INFO1, None, True],
    # 1.2. булевое значение
    [BAD_SAVE_INFO2, None, True],
    # 1.3. None
    [BAD_SAVE_INFO3, None, True],
    # 2. неверный тип у triplets
    # 2.1. строка
    [BAD_SAVE_INFO4, None, True],
    # 2.2. список из строк
    [BAD_SAVE_INFO5, None, True],
    # 3. пустой triplets
    [SAVE_INFO1, {EPISODIC_TRIPLET1.id: {'456'}, HYPER_TRIPLET2.id: {'456'}}, False],
    # 4. такой text_id уже существует
    [SAVE_INFO2, {SIMPLE_TRIPLET1.id: {'123'}, SIMPLE_TRIPLET2.id: {'123'}}, False],
    # 5. У двух text_id ->
    # 5.1. пересекается один триплет
    [SAVE_INFO3, {SIMPLE_TRIPLET1.id: {'123', '456'}, SIMPLE_TRIPLET2.id: {'123'}}, False],
    # 5.2. пересекается два триплета
    [SAVE_INFO4, {SIMPLE_TRIPLET1.id: {'123', '456'}, SIMPLE_TRIPLET2.id: {'123', '456'}}, False],
    # 5.3. пересекается три триплета
    [SAVE_INFO5, {SIMPLE_TRIPLET1.id: {'123', '456'}, SIMPLE_TRIPLET2.id: {'123', '456'}, HYPER_TRIPLET1.id: {'123', '456'}}, False],
    # 5.4. нет пересекающихся триплетов
    [SAVE_INFO6, {SIMPLE_TRIPLET1.id: {'123'}, SIMPLE_TRIPLET2.id: {'456'}}, False],
    # 6. У трёх text_id ->
    # 6.1. пересекается один триплет
    [SAVE_INFO7, {SIMPLE_TRIPLET1.id: {'123', '456', '789'}}, False],
    # 6.2. пересекается два триплета
    [SAVE_INFO8, {SIMPLE_TRIPLET1.id: {'123', '456', '789'}, SIMPLE_TRIPLET2.id: {'123', '456', '789'}}, False],
    # 6.3. пересекается три триплета
    [SAVE_INFO9, {SIMPLE_TRIPLET1.id: {'123', '456', '789'}, SIMPLE_TRIPLET2.id: {'123', '456', '789'}, HYPER_TRIPLET1.id: {'123', '456', '789'}}, False],
    # 6.4. нет пересекающихся триплетов
    [SAVE_INFO10, {SIMPLE_TRIPLET1.id: {'123'}, SIMPLE_TRIPLET2.id: {'456'}, HYPER_TRIPLET2.id: {'789'}}, False]
]

STORE_POPULATED_SAVE_TEST_CASES = []
for db_vendor in AVAILABLE_KV_DBS:
    for i in range(len(STORE_SAVE_TEST_CASES)):
        STORE_POPULATED_SAVE_TEST_CASES.append(
            STORE_SAVE_TEST_CASES[i] + [db_vendor])

###############################################################################################

# save_info, triplet_id, expected_texts_info, exception, textidstore_instance
STORE_LOAD_TEST_CASES = [
    # 1. неверный тип у triplet_id
    # 1.1. число
    [SAVE_INFO3, 123, None, True],
    # 1.2. булевое значение
    [SAVE_INFO3, False, None, True],
    # 1.3. None
    [SAVE_INFO3, None, None, True],
    # 2. такого triplet_id не существует
    [SAVE_INFO3, '789', None, True],
    # 3. позитивный тест
    # 3.1. получение одного text_id
    [SAVE_INFO3, SIMPLE_TRIPLET2.id, {'123'}, False],
    # 3.2. получение нескольких text_id
    [SAVE_INFO3, SIMPLE_TRIPLET1.id, {'123', '456'}, False]
]

STORE_POPULATED_LOAD_TEST_CASES = []
for db_vendor in AVAILABLE_KV_DBS:
    for i in range(len(STORE_LOAD_TEST_CASES)):
        STORE_POPULATED_LOAD_TEST_CASES.append(
            STORE_LOAD_TEST_CASES[i] + [db_vendor])
