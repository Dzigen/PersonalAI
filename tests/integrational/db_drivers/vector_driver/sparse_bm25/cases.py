import torch
import numpy
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
TEST_VOLUME_DIR = './volumes'
sys.path.insert(0, PROJECT_BASE_DIR)

from src.db_drivers.vector_driver import VectorDBInstance

# TO CHANGE
AVAILABLE_BM25_DBS = ['weaviate']  # 'opensearch', 'elasticsearch', 'inmemory', 'weaviate'

###############################################################################################

FULL_INSTANCE1 = VectorDBInstance(id='123', document='qwerty' , metadata={'k1': 'v1'})
FULL_INSTANCE2 = VectorDBInstance(id='456', document='ytrewq', metadata={'k2': 'v2'})

INSTANSE_W_BAD_EMB = VectorDBInstance(id='789', document='ytrewq', embedding=[0.1,0.4,0.7], metadata={'k3': 'v3'}) # !!! CARE !!!

UPDATE_FULL_INSTANCE1 = VectorDBInstance(id='123', document='qwerty qwerty', metadata={'k1new': 'v1new'})
UPDATE_FULL_INSTANCE2 = VectorDBInstance(id='456', document='ytrewq ytrewq', metadata={'k2new': 'v2new'})

INSTANCE_WO_METADATA = VectorDBInstance(id='456', document='ytrewq')
INSTANCE_WO_ID = VectorDBInstance(document='ytrewq')

INSTANCE_WITH_BAD_ID1 = VectorDBInstance(id=123, document='qwerty')
INSTANCE_WITH_BAD_ID2 = VectorDBInstance(id=True, document='qwerty')
INSTANCE_WITH_BAD_ID3 = VectorDBInstance(id=None, document='qwerty')

###############################################################################################

# input, expected
BM25_CREATE_TEST_CASES = [
    # 1. пустой список
    [[[]], {'exception': False, 'db_size': 0}],
    # 2. один элемент с метаданными
    [[[FULL_INSTANCE1]], {'exception': False, 'db_size': 1}],
    # 3. один элемент без метаданных
    [[[INSTANCE_WO_METADATA]], {'exception': False, 'db_size': 1}],
    # 4. один элемент без идентификатора
    [[[INSTANCE_WO_ID]], {'exception': True, 'db_size': 0}],
    # 5. embedding-поле не пустое
    [[[INSTANSE_W_BAD_EMB]], {'exception': True, 'db_size': 0}],
    # 6. несколько элементов
    [[[FULL_INSTANCE1, FULL_INSTANCE2]], {'exception': False, 'db_size': 2}],
    # 7. дубликаты в списке
    [[[FULL_INSTANCE1, FULL_INSTANCE1]], {'exception': True, 'db_size': 0}],
    # 8. элемент существует в бд (по id)
    [[[FULL_INSTANCE1], [FULL_INSTANCE1]], {'exception': False, 'db_size': 1}],
    # 9. неверный формат идентикатора 1
    [[[INSTANCE_WITH_BAD_ID1]], {'exception': True, 'db_size': 0}],
    # 10. неверный формат идентификатора 2
    [[[INSTANCE_WITH_BAD_ID2]], {'exception': True, 'db_size': 0}],
    # 11. неверный формат идентификатора 3
    [[[INSTANCE_WITH_BAD_ID3]], {'exception': True, 'db_size': 0}]
]

BM25_POPULATED_CREATE_TEST_CASES = []
for db_vendor in AVAILABLE_BM25_DBS:
    for i in range(len(BM25_CREATE_TEST_CASES)):
        BM25_POPULATED_CREATE_TEST_CASES.append(
            BM25_CREATE_TEST_CASES[i] + [db_vendor])

###############################################################################################

# instances, delete_ids, expected
BM25_DELETE_TEST_CASES = [
    # 1. пустой список
    [[FULL_INSTANCE1, FULL_INSTANCE2], [], {'exception': False, 'db_size': 2}],
    # 2. удаление одного существующего элемента
    [[FULL_INSTANCE1, FULL_INSTANCE2], ['456'],
        {'exception': False, 'db_size': 1}],
    # 3. удаление одного несуществующего элемента
    [[FULL_INSTANCE1, FULL_INSTANCE2], ['789'],
        {'exception': False, 'db_size': 2}],
    # 4. в списке элементов на удаление есть несуществующие
    [[FULL_INSTANCE1, FULL_INSTANCE2], ['456', '789'],
        {'exception': False, 'db_size': 1}],
    # 5. в списке элементов на удаление все существуют
    [[FULL_INSTANCE1, FULL_INSTANCE2], ['123', '456'],
        {'exception': False, 'db_size': 0}],
    # 6. неверный формат идентификаторов 1
    [[FULL_INSTANCE1, FULL_INSTANCE2], [123],
        {'exception': True, 'db_size': 2}],
    # 7. неверный формат идентификатора 2
    [[FULL_INSTANCE1, FULL_INSTANCE2], [True],
        {'exception': True, 'db_size': 2}],
    # 8. неверный формат идентификатора 3
    [[FULL_INSTANCE1, FULL_INSTANCE2], [None],
        {'exception': True, 'db_size': 2}]
]

BM25_POPULATED_DELETE_TEST_CASES = []
for db_vendor in AVAILABLE_BM25_DBS:
    for i in range(len(BM25_DELETE_TEST_CASES)):
        BM25_POPULATED_DELETE_TEST_CASES.append(
            BM25_DELETE_TEST_CASES[i] + [db_vendor])

###############################################################################################

# instances, input, expected
BM25_READ_TEST_CASES = [
    # 1. пустой список
    [[FULL_INSTANCE1, FULL_INSTANCE2], [], {
        'exception': False, 'output_ids': []}],
    # 2. один существующий элемент
    [[FULL_INSTANCE1, FULL_INSTANCE2], ['123'], {
        'exception': False, 'output_ids': ['123']}],
    # 3. один несуществующий элемент
    [[FULL_INSTANCE1, FULL_INSTANCE2], ['789'],
        {'exception': False, 'output_ids': []}],
    # 4. несколько существующих элементов
    [[FULL_INSTANCE1, FULL_INSTANCE2], ['123', '456'], {
        'exception': False, 'output_ids': ['123', '456']}],
    # 5. в списке есть несуществующий элемент
    [[FULL_INSTANCE1, FULL_INSTANCE2], ['123', '789', '456'],
        {'exception': False, 'output_ids': ['123', '456']}],
    # 6. неверный формат идентификаторов 1
    [[FULL_INSTANCE1, FULL_INSTANCE2], [123], {
        'exception': True, 'output_ids': []}],
    # 7. неверный формат идентификатора 2
    [[FULL_INSTANCE1, FULL_INSTANCE2], [True],
        {'exception': True, 'output_ids': []}],
    # 8. неверный формат идентификатора 3
    [[FULL_INSTANCE1, FULL_INSTANCE2], [None],
        {'exception': True, 'output_ids': []}]
]

BM25_POPULATED_READ_TEST_CASES = []
for db_vendor in AVAILABLE_BM25_DBS:
    for i in range(len(BM25_READ_TEST_CASES)):
        BM25_POPULATED_READ_TEST_CASES.append(
            BM25_READ_TEST_CASES[i] + [db_vendor])

###############################################################################################

BM25_UPDATE_TEST_CASES = [
    # TODO
]

###############################################################################################

# init_instance, new_instances, exception, expected_count
BM25_UPSERT_TEST_CASES = [
    # элемент добавляется с нуля
    [[FULL_INSTANCE1], {FULL_INSTANCE2.id: FULL_INSTANCE2}, False, 2],
    # элемент обновляется
    [[FULL_INSTANCE1, FULL_INSTANCE2], {
        UPDATE_FULL_INSTANCE2.id: UPDATE_FULL_INSTANCE2}, False, 2],
    # несколько элементов (один добавляется, другой обновляется)
    [[FULL_INSTANCE1], {FULL_INSTANCE2.id: FULL_INSTANCE2,
                        UPDATE_FULL_INSTANCE1.id: UPDATE_FULL_INSTANCE1}, False, 2]
]

BM25_POPULATED_UPSERT_TEST_CASES = []
for db_vendor in AVAILABLE_BM25_DBS:
    for i in range(len(BM25_UPSERT_TEST_CASES)):
        BM25_POPULATED_UPSERT_TEST_CASES.append(
            BM25_UPSERT_TEST_CASES[i] + [db_vendor])

###############################################################################################

# instances, queries, n_results, subset_ids, expected
BM25_RETRIEVE_TEST_CASES = [
    # 1.1 ретрив по одному квери
    [[FULL_INSTANCE1, FULL_INSTANCE2], [FULL_INSTANCE1],1, None, {'exception': False, 'output_size': 1}],
    # 1.2 ретрив по одному квери (из подмножества)
    [[FULL_INSTANCE1, FULL_INSTANCE2], [FULL_INSTANCE1], 2, [FULL_INSTANCE1.id], {'exception': False, 'output_size': 1}],
    # 2. ретрив по нескольким квери
    [[FULL_INSTANCE1, FULL_INSTANCE2], [FULL_INSTANCE1, FULL_INSTANCE1], 1, None, {'exception': False, 'output_size': 1}],
    # 3. в бд меньше элементов, чем заданное количество
    [[FULL_INSTANCE1], [FULL_INSTANCE1], 2, None, {'exception': False, 'output_size': 1}],
    # 4. embedding-поле не пустое
    [[FULL_INSTANCE1, FULL_INSTANCE2], [INSTANSE_W_BAD_EMB], 1, None, {'exception': False, 'output_size': 1}],
    # 5. В векторной бд нуль объектов
    [[], [FULL_INSTANCE1], 2, None, {'exception': False, 'output_size': 0}]
]

BM25_POPULATED_RETRIEVE_TEST_CASES = []
for db_vendor in AVAILABLE_BM25_DBS:
    for i in range(len(BM25_RETRIEVE_TEST_CASES)):
        BM25_POPULATED_RETRIEVE_TEST_CASES.append(
            BM25_RETRIEVE_TEST_CASES[i] + [db_vendor])

###############################################################################################

# instances, expected
BM25_COUNT_TEST_CASES = [
    # 1. нуль элементов
    [[], 0],
    # 2. один Элемент
    [[FULL_INSTANCE1], 1],
    # 3. несколько элементов
    [[FULL_INSTANCE1, FULL_INSTANCE2], 2]
]

BM25_POPULATED_COUNT_TEST_CASES = []
for db_vendor in AVAILABLE_BM25_DBS:
    for i in range(len(BM25_COUNT_TEST_CASES)):
        BM25_POPULATED_COUNT_TEST_CASES.append(
            BM25_COUNT_TEST_CASES[i] + [db_vendor])

###############################################################################################

# instances, input_id, expected
BM25_EXIST_TEST_CASES = [
    # 1. элемент существует
    [[FULL_INSTANCE1, FULL_INSTANCE2], '123',
        {'exception': False, 'exist': True}],
    # 2. элемента не существует
    [[FULL_INSTANCE1, FULL_INSTANCE2], '789',
        {'exception': False, 'exist': False}],
    # 3. неверный формат идентификатора # 1
    [[FULL_INSTANCE1, FULL_INSTANCE2], 789, {
        'exception': True, 'exist': False}],
    # 4. неверный формат идентификатора # 2
    [[FULL_INSTANCE1, FULL_INSTANCE2], False,
        {'exception': True, 'exist': False}],
    # 5. неверный формат идентификатора # 3
    [[FULL_INSTANCE1, FULL_INSTANCE2], None,
        {'exception': True, 'exist': False}]
]

BM25_POPULATED_EXIST_TEST_CASES = []
for db_vendor in AVAILABLE_BM25_DBS:
    for i in range(len(BM25_EXIST_TEST_CASES)):
        BM25_POPULATED_EXIST_TEST_CASES.append(
            BM25_EXIST_TEST_CASES[i] + [db_vendor])

###############################################################################################

# instances
BM25_CLEAR_TEST_CASES = [
    # 1. чистка пустой бд
    [[]],
    # 2. чиста бд с одним элементов
    [[FULL_INSTANCE1]],
    # 3. чиста бд с несколькими элементами
    [[FULL_INSTANCE1, FULL_INSTANCE2]]
]

BM25_POPULATED_CLEAR_TEST_CASES = []
for db_vendor in AVAILABLE_BM25_DBS:
    for i in range(len(BM25_CLEAR_TEST_CASES)):
        BM25_POPULATED_CLEAR_TEST_CASES.append(
            BM25_CLEAR_TEST_CASES[i] + [db_vendor])
