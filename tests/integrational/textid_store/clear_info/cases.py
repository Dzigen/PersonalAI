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

SAVE_INFO1 = [['123', [SIMPLE_TRIPLET1, SIMPLE_TRIPLET2]], ['456', [HYPER_TRIPLET1, HYPER_TRIPLET2]]]
SAVE_INFO2 = [['123', [SIMPLE_TRIPLET1, SIMPLE_TRIPLET2]], ['456', [HYPER_TRIPLET1, SIMPLE_TRIPLET1]]]
SAVE_INFO3 = [['123', [SIMPLE_TRIPLET1, SIMPLE_TRIPLET2]], ['456', [SIMPLE_TRIPLET1, SIMPLE_TRIPLET2]]]

###############################################################################################

# save_info, text_id, expected_deleted_tripeltsid, expected_updated_tripeltsid, exception, textidstore_instance
STORE_CLEARINFO_TEST_CASES = [
    # 1. неверный тип у text_id
    # 1.1. число
    [SAVE_INFO1, 123, None, None, True],
    # 1.2. булевое значение
    [SAVE_INFO1, False, None, None, True],
    # 1.3. None
    [SAVE_INFO1, None, None, None, True],
    # 2. удаляются все triplettotexts-записи для заданного text_id
    [SAVE_INFO1, '123', {SIMPLE_TRIPLET1.id, SIMPLE_TRIPLET2.id}, set(), False],
    # 3. часть triplettotexts-записей обновляется для заданного text_id
    [SAVE_INFO2, '123', {SIMPLE_TRIPLET2.id}, {SIMPLE_TRIPLET1.id}, False],
    # 4. все triplettotexts-записи обновляются для заданного text_id
    [SAVE_INFO3, '123', set(), {SIMPLE_TRIPLET1.id, SIMPLE_TRIPLET2.id}, False]
]

STORE_POPULATED_CLEARINFO_TEST_CASES = []
for db_vendor in AVAILABLE_KV_DBS:
    for i in range(len(STORE_CLEARINFO_TEST_CASES)):
        STORE_POPULATED_CLEARINFO_TEST_CASES.append(
            STORE_CLEARINFO_TEST_CASES[i] + [db_vendor])
