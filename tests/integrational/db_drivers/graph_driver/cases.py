import sys
sys.path.insert(0, "../../../")
from src.utils.data_structs import Triplet, NodeCreator, Relation, RelationType, NodeType
from src.utils.errors import ReturnInfo

# nodes
OBJECT_NODE1 = NodeCreator.create(name='abc', type=NodeType.object, prop={'k1': 'v1'})
OBJECT_NODE2 = NodeCreator.create(name='def', type=NodeType.object, prop={'k2': 'v2'})
OBJECT_NODE3 = NodeCreator.create(name='ghi', type=NodeType.object, prop={'k3': 'v3'})
OBJECT_NODE4 = NodeCreator.create(name='yhn', type=NodeType.object, prop={'k13': 'v13'})

THESIS_NODE1 = NodeCreator.create(name='qwerty', type=NodeType.hyper, prop={'k4': 'v4'})
THESIS_NODE2 = NodeCreator.create(name='asdfgh', type=NodeType.hyper, prop={'k5': 'v5'})
THESIS_NODE3 = NodeCreator.create(name='zxcvbn', type=NodeType.hyper, prop={'k6': 'v6'})

EPISODIC_NODE1 = NodeCreator.create(name='uiop', type=NodeType.episodic, prop={'k7': 'v7'})
EPISODIC_NODE2 = NodeCreator.create(name='jkl', type=NodeType.episodic, prop={'k8': 'v8'})
EPISODIC_NODE3 = NodeCreator.create(name='mnbv', type=NodeType.episodic, prop={'k9': 'v9'})

# triplets
SIMPLE_TRIPLET1 = Triplet(start_node=OBJECT_NODE1, relation=Relation(name='simple1', type=RelationType.hyper, prop={'k10': 'v10'}), end_node=OBJECT_NODE2)
SIMPLE_TRIPLET2 = Triplet(start_node=OBJECT_NODE2, relation=Relation(name='simple2', type=RelationType.hyper, prop={'k11': 'v11'}), end_node=OBJECT_NODE3)
SIMPLE_TRIPLET3 = Triplet(start_node=OBJECT_NODE3, relation=Relation(name='simple3', type=RelationType.hyper, prop={'k12': 'v12'}), end_node=OBJECT_NODE1)
SIMPLE_TRIPLET4 = Triplet(start_node=OBJECT_NODE3, relation=Relation(name='simple4', type=RelationType.hyper, prop={'k14': 'v14'}), end_node=OBJECT_NODE4)

THESIS_TRIPLET1 = Triplet(start_node=OBJECT_NODE1, relation=Relation(name='hyper', type=RelationType.hyper), end_node=THESIS_NODE1)
THESIS_TRIPLET2 = Triplet(start_node=OBJECT_NODE2, relation=Relation(name='hyper', type=RelationType.hyper), end_node=THESIS_NODE1)
THESIS_TRIPLET3 =Triplet(start_node=OBJECT_NODE3, relation=Relation(name='hyper', type=RelationType.hyper), end_node=THESIS_NODE2)


EPISODIC_TRIPLET1 = Triplet(start_node=OBJECT_NODE1, relation=Relation(name='episodic', type=RelationType.episodic), end_node=EPISODIC_NODE1)
EPISODIC_TRIPLET2 = Triplet(start_node=OBJECT_NODE2, relation=Relation(name='episodic', type=RelationType.episodic), end_node=EPISODIC_NODE1)
EPISODIC_TRIPLET3 = Triplet(start_node=OBJECT_NODE3, relation=Relation(name='episodic', type=RelationType.episodic), end_node=EPISODIC_NODE2)
EPISODIC_TRIPLET4 = Triplet(start_node=THESIS_NODE2, relation=Relation(name='episodic', type=RelationType.episodic), end_node=EPISODIC_NODE2)

# creation info
FULL_CREATION_INFO = {'s_node': True, 'rel': True, 'e_node': True}
WO_SN_CREATION_INFO = {'s_node': False, 'rel': True, 'e_node': True}
WO_EN_CREATION_INFO = {'s_node': True, 'rel': True, 'e_node': False}
ONLY_REL_CREATION_INFO = {'s_node': False, 'rel': True, 'e_node': False}

# ======================================================================

GRAPHB_CREAT_TEST_CASES = [
    # 1. пустой список
    ([[]], {'exception': False, 'db_size': 0}),
    # 2. добавление одного триплета (полностью с creation_info None)
    # 2.1 simple
    ([[SIMPLE_TRIPLET1]], [[None]], {'exception': False, 'triplets_count': 1, 'nodes_count': 2}),
    # 2.2 thesis
    ([[THESIS_TRIPLET2]], [[None]], {'exception': False, 'triplets_count': 1, 'nodes_count': 2}),
    # 2.3 episodic with object
    ([[EPISODIC_TRIPLET1]], [[None]], {'exception': False, 'triplets_count': 1, 'nodes_count': 2}),
    # 2.4 episodic with thesis
    ([[EPISODIC_TRIPLET4]], [[None]], {'exception': False, 'triplets_count': 1, 'nodes_count': 2}),

    # 3. добавление одного триплета (полностью с creation_info не None)
    # 3.1 simple
    ([[SIMPLE_TRIPLET1]], [[FULL_CREATION_INFO]], {'exception': False, 'triplets_count': 1, 'nodes_count': 2}),
    # 3.2 thesis
    ([[THESIS_TRIPLET2]], [[FULL_CREATION_INFO]], {'exception': False, 'triplets_count': 1, 'nodes_count': 2}),
    # 3.3 episodic with object
    ([[EPISODIC_TRIPLET1]], [[FULL_CREATION_INFO]], {'exception': False, 'triplets_count': 1, 'nodes_count': 2}),
    # 3.4 episodic with thesis
    ([[EPISODIC_TRIPLET4]], [[FULL_CREATION_INFO]], {'exception': False, 'triplets_count': 1, 'nodes_count': 2}),

    # 4. добалвение одного триплета (только связь c заданным creation_info)
    # 4.1 simple rel
    ([[SIMPLE_TRIPLET1, SIMPLE_TRIPLET2],[SIMPLE_TRIPLET3]], [[FULL_CREATION_INFO, WO_SN_CREATION_INFO], [ONLY_REL_CREATION_INFO]], {'exception': False, 'triplets_count': 3, 'nodes_count': 3}),
    # 4.2 hyper (object with thesis)
    ([[SIMPLE_TRIPLET2, THESIS_TRIPLET1],[THESIS_TRIPLET2]], [[FULL_CREATION_INFO, WO_SN_CREATION_INFO], [ONLY_REL_CREATION_INFO]], {'exception': False, 'triplets_count': 3, 'nodes_count': 3}),
    # 4.3 episodic (object with episodic)
    ([[SIMPLE_TRIPLET1, EPISODIC_TRIPLET1],[EPISODIC_TRIPLET2]], [[FULL_CREATION_INFO, WO_SN_CREATION_INFO], [ONLY_REL_CREATION_INFO]], {'exception': False, 'triplets_count': 3, 'nodes_count': 3}),
    # 4.4 episodic (thesis with episodic)
    ([[EPISODIC_TRIPLET3, THESIS_TRIPLET3],[EPISODIC_TRIPLET4]], [[FULL_CREATION_INFO, WO_SN_CREATION_INFO], [ONLY_REL_CREATION_INFO]], {'exception': False, 'triplets_count': 3, 'nodes_count': 3}),

    # 5. добавление одного триплета (связь и стартовая вершина c заданным creation_info)
    # 5.1 object -[simple]> object
    ([[SIMPLE_TRIPLET2], [SIMPLE_TRIPLET1]], [[FULL_CREATION_INFO],[WO_EN_CREATION_INFO]], {'exception': False, 'triplet_count': 2, 'nodes_count': 2}),
    # 5.2 object -[hyper]> thesis
    ([[THESIS_TRIPLET2], [THESIS_TRIPLET1]], [[FULL_CREATION_INFO],[WO_EN_CREATION_INFO]], {'exception': False, 'triplet_count': 2, 'nodes_count': 2}),
    # 5.3 object -[episodic]> episodic
    ([[EPISODIC_TRIPLET2], [EPISODIC_TRIPLET1]], [[FULL_CREATION_INFO],[WO_EN_CREATION_INFO]], {'exception': False, 'triplet_count': 2, 'nodes_count': 2}),
    # 5.4 thesis -[episodic]> episodic
    ([[EPISODIC_TRIPLET3], [EPISODIC_TRIPLET4]], [[FULL_CREATION_INFO],[WO_EN_CREATION_INFO]], {'exception': False, 'triplet_count': 2, 'nodes_count': 2}),

    # 6. добавление одного триплета (связь и конечная вершина c заданным creation_info)
    # 6.1 object <[simple]- object
    ([[SIMPLE_TRIPLET1], [SIMPLE_TRIPLET2]], [[FULL_CREATION_INFO],[WO_SN_CREATION_INFO]], {'exception': False, 'triplet_count': 2, 'nodes_count': 2}),
    # 6.2 thesis <[hyper]- object
    ([[SIMPLE_TRIPLET1], [THESIS_TRIPLET1]], [[FULL_CREATION_INFO],[WO_SN_CREATION_INFO]], {'exception': False, 'triplet_count': 2, 'nodes_count': 2}),
    # 6.3 episodic <[episodic]- object
    ([[SIMPLE_TRIPLET1], [EPISODIC_TRIPLET1]], [[FULL_CREATION_INFO],[WO_SN_CREATION_INFO]], {'exception': False, 'triplet_count': 2, 'nodes_count': 2}),
    # 6.4 episodic <[episodic]- thesis
    ([[THESIS_TRIPLET3], [EPISODIC_TRIPLET4]], [[FULL_CREATION_INFO],[WO_SN_CREATION_INFO]], {'exception': False, 'triplet_count': 2, 'nodes_count': 2}),

    # 7. добавление несколько разных триплетов (полностью c заданным creation_info)
    # 7.1 simple and simple
    ([[SIMPLE_TRIPLET1, SIMPLE_TRIPLET4]], [[FULL_CREATION_INFO, FULL_CREATION_INFO]], {'exception': False, 'triplet_count': 2, 'nodes_count': 4}),
    # 7.2 simple and hyper
    ([[SIMPLE_TRIPLET1, THESIS_TRIPLET3]], [[FULL_CREATION_INFO, FULL_CREATION_INFO]], {'exception': False, 'triplet_count': 2, 'nodes_count': 4}),
    # 7.3 hyper and episodic
    ([[THESIS_TRIPLET1, EPISODIC_TRIPLET2]], [[FULL_CREATION_INFO, FULL_CREATION_INFO]], {'exception': False, 'triplet_count': 2, 'nodes_count': 4}),
    # 7.4 simple and episodic
    ([[SIMPLE_TRIPLET4, EPISODIC_TRIPLET1]], [[FULL_CREATION_INFO, FULL_CREATION_INFO]], {'exception': False, 'triplet_count': 2, 'nodes_count': 4}),

    # 8. добавление несколькиз связанных триплетов без creation info
    ([[SIMPLE_TRIPLET1, SIMPLE_TRIPLET2]], [[None, None]], {'exception': False, 'triplet_count': 2, 'nodes_count': 4}),
]

GRAPHB_DELETE_TEST_CASES = [
    # 1. пустой список
    ([SIMPLE_TRIPLET3, SIMPLE_TRIPLET4], [FULL_CREATION_INFO, WO_SN_CREATION_INFO], [], {'exception': False, 'triplet_count': 2, 'nodes_count': 3}),
    # 2. один существующий триплет (удаляется связь и вершины)
    ([SIMPLE_TRIPLET1, SIMPLE_TRIPLET4], [FULL_CREATION_INFO, FULL_CREATION_INFO], [SIMPLE_TRIPLET1.id], {'exception': False, 'triplet_count': 1, 'nodes_count': 2}),
    # 3. один существующий триплет (удаляется только связь)
    ([SIMPLE_TRIPLET1, SIMPLE_TRIPLET2, SIMPLE_TRIPLET3], [FULL_CREATION_INFO, WO_SN_CREATION_INFO, ONLY_REL_CREATION_INFO], [SIMPLE_TRIPLET3.id], {'exception': False, 'triplet_count': 2, 'nodes_count': 3}),
    # 4. один несуществующий триплет
    ([SIMPLE_TRIPLET1], [FULL_CREATION_INFO], [SIMPLE_TRIPLET2.id], {'exception': False, 'triplet_count': 1, 'nodes_count': 2}),
    # 5. несколько триплетов (на удаление связи; связи и вершины; связи и вершин)
    ([SIMPLE_TRIPLET1, SIMPLE_TRIPLET3, THESIS_TRIPLET2, EPISODIC_TRIPLET2], [FULL_CREATION_INFO, WO_EN_CREATION_INFO, WO_SN_CREATION_INFO, WO_SN_CREATION_INFO], [SIMPLE_TRIPLET1.id, THESIS_TRIPLET2.id, EPISODIC_TRIPLET2.id], {'exception': False, 'triplet_count': 1, 'nodes_count': 2}),
    # 6. несколько триплетов (на удаление связи; удаление несуществующего триплета; удаление связи и вершины)
    ([SIMPLE_TRIPLET1, SIMPLE_TRIPLET3, THESIS_TRIPLET2, EPISODIC_TRIPLET2], [FULL_CREATION_INFO, WO_EN_CREATION_INFO, WO_SN_CREATION_INFO, WO_SN_CREATION_INFO], [SIMPLE_TRIPLET1.id, 'unknow_id', THESIS_TRIPLET2.id], {'exception': False, 'triplet_count': 2, 'nodes_count': 4}),
    # 7. неверный формат идентификатора 1
    ([SIMPLE_TRIPLET1], [FULL_CREATION_INFO], [123], {'exception': True, 'triplet_count': 1, 'nodes_count': 2}),
    # 8. неверный формат идентификатора 2
    ([SIMPLE_TRIPLET1], [FULL_CREATION_INFO], [True], {'exception': True, 'triplet_count': 1, 'nodes_count': 2}),
    # 9. неверный формат идентификатора 3
    ([SIMPLE_TRIPLET1], [FULL_CREATION_INFO], [None], {'exception': True, 'triplet_count': 1, 'nodes_count': 2}),
]

GRAPHB_READ_TEST_CASES = [
    # 1. пустой список
    ([SIMPLE_TRIPLET1,SIMPLE_TRIPLET2], [FULL_CREATION_INFO, WO_SN_CREATION_INFO], [], {'exception': False, 'output_ids': []}),
    # 2. один существующий триплет
    ([SIMPLE_TRIPLET1,SIMPLE_TRIPLET2], [FULL_CREATION_INFO, WO_SN_CREATION_INFO], [SIMPLE_TRIPLET1.id], {'exception': False, 'output_ids': [SIMPLE_TRIPLET1.id]}),
    # 3. один несуществующий триплет
    ([SIMPLE_TRIPLET1,SIMPLE_TRIPLET2], [FULL_CREATION_INFO, WO_SN_CREATION_INFO], [SIMPLE_TRIPLET3.id], {'exception': False, 'output_ids': []}),
    # 4. несколько существующих триплетов
    ([SIMPLE_TRIPLET1,SIMPLE_TRIPLET2], [FULL_CREATION_INFO, WO_SN_CREATION_INFO], [SIMPLE_TRIPLET1.id, SIMPLE_TRIPLET2.id], {'exception': False, 'output_ids': [SIMPLE_TRIPLET1.id, SIMPLE_TRIPLET2.id]}),
    # 5. в списке есть несуществующий триплет
    ([SIMPLE_TRIPLET1,SIMPLE_TRIPLET2], [FULL_CREATION_INFO, WO_SN_CREATION_INFO], [SIMPLE_TRIPLET1.id, SIMPLE_TRIPLET3.id], {'exception': False, 'output_ids': [SIMPLE_TRIPLET1.id, SIMPLE_TRIPLET2.id]}),
    # 6. неверный формат идентификатора 1
    ([SIMPLE_TRIPLET1,SIMPLE_TRIPLET2], [FULL_CREATION_INFO, WO_SN_CREATION_INFO], [123], {'exception': True, 'output_ids': []}),
    # 7. неверный формат идентификатора 2
    ([SIMPLE_TRIPLET1,SIMPLE_TRIPLET2], [FULL_CREATION_INFO, WO_SN_CREATION_INFO], [True], {'exception': True, 'output_ids': []}),
    # 8. неверный формат идентификатора 3
    ([SIMPLE_TRIPLET1,SIMPLE_TRIPLET2], [FULL_CREATION_INFO, WO_SN_CREATION_INFO], [None], {'exception': True, 'output_ids': []}),
]

GRAPHB_COUNT_TEST_CASES = [
    # 1. нуль элементов
    ([], [None], {'triplets_count': 0, 'nodes_count': 0}),
    # 2. один элемент
    ([SIMPLE_TRIPLET1], [None], {'triplets_count': 1, 'nodes_count': 2}),
    # 3. несколько элементов с creation_info = None
    ([SIMPLE_TRIPLET1,SIMPLE_TRIPLET1], [None, None], {'triplets_count': 2, 'nodes_count': 4})
    # 4. несколько элементов с меками объектов-дубликатов (creation_info != None)
    ([SIMPLE_TRIPLET1, SIMPLE_TRIPLET2], [FULL_CREATION_INFO, WO_SN_CREATION_INFO], {'triplets_count': 2, 'nodes_count': 3})
]

GRAPHB_EXIST_TEST_CASES = [
    # 1. элемент существует
    ([SIMPLE_TRIPLET1, EPISODIC_TRIPLET3], SIMPLE_TRIPLET1.id, {'exception': False, 'exist': True}),
    # 2. элемента не существует
    ([SIMPLE_TRIPLET1, EPISODIC_TRIPLET3], 'unknown_id', {'exception': False, 'exist': False}),
    # 3. неверный формат идентификатора # 1
    ([SIMPLE_TRIPLET1, EPISODIC_TRIPLET3], 789, {'exception': True, 'exist': False}),
    # 4. неверный формат идентификатора # 2
    ([SIMPLE_TRIPLET1, EPISODIC_TRIPLET3], False, {'exception': True, 'exist': False}),
    # 5. неверный формат идентификатора # 3
    ([SIMPLE_TRIPLET1, EPISODIC_TRIPLET3], None, {'exception': True, 'exist': False})
]

GRAPHB_CLEAR_TEST_CASES = [
    # 1. чистка пустой бд
    ([], {'triplets_count': 0, 'nodes_count': 0}),
    # 2. чистка бд с одним триплетом
    # 2.1. simple
    ([SIMPLE_TRIPLET1], {'triplets_count': 1, 'nodes_count': 2}),
    # 2.2. thesis with object
    ([THESIS_TRIPLET1], {'triplets_count': 1, 'nodes_count': 2}),
    # 2.3. episodic with object
    ([EPISODIC_TRIPLET1], {'triplets_count': 1, 'nodes_count': 2}),
    # 2.4. episodic with thesis
    ([EPISODIC_TRIPLET4], {'triplets_count': 1, 'nodes_count': 2}),
    # 3. чиста бд с несколькими элементами
    ([SIMPLE_TRIPLET1, THESIS_TRIPLET1, EPISODIC_TRIPLET1, EPISODIC_TRIPLET4], {'triplets_count': 4, 'nodes_count': 8})
]
