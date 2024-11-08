from chromadb.errors import ChromaError
import torch
import numpy

import sys
sys.path.insert(0, "../../../")
from src.db_drivers.vector_driver import VectorDBInstance
from src.utils.errors import ReturnInfo

FULL_INSTANCE1 = VectorDBInstance(id='123', document='qwerty', embedding=[0.1,0.2,0.3], metadata={'k1': 'v1'})
FULL_INSTANCE2 = VectorDBInstance(id='456', document='ytrewq', embedding=[0.4,0.5,0.6], metadata={'k2': 'v2'})
INSTANCE_WO_METADATA = VectorDBInstance(id='456', document='ytrewq', embedding=[0.4,0.5,0.6])
INSTANCE_WO_ID = VectorDBInstance(document='ytrewq', embedding=[0.4,0.5,0.6])
INSTANCE_WO_EMBEDDING = VectorDBInstance(id='456', document='ytrewq')

INSTANCE_WITH_BAD_ID1 = VectorDBInstance(id=123, document='qwerty', embedding=[0.1,0.2,0.3])
INSTANCE_WITH_BAD_ID2 = VectorDBInstance(id=True, document='qwerty', embedding=[0.1,0.2,0.3])
INSTANCE_WITH_BAD_ID3 = VectorDBInstance(id=None, document='qwerty', embedding=[0.1,0.2,0.3])

INSTANCE_WITH_TORCH_EMB = VectorDBInstance(id='123', document='qwerty', embedding=torch.tensor([0.1,0.2,0.3]), metadata={'k1': 'v1'})
INSTANCE_WITH_NUMPY_EMB = VectorDBInstance(id='123', document='qwerty', embedding=numpy.array([0.1,0.2,0.3]), metadata={'k1': 'v1'})

INSTANCE_WITH_BAD_EMB1 = VectorDBInstance(id='456', document='ytrewq', embedding="[0.4,0.5,0.6]")
INSTANCE_WITH_BAD_EMB2 = VectorDBInstance(id='456', document='ytrewq', embedding=None)
INSTANCE_WITH_BAD_EMB3 = VectorDBInstance(id='456', document='ytrewq', embedding=[[0.4,0.5,0.6]])

VECTORDB_CREAT_TEST_CASES = [
    # пустой список
    ([[]], {'info': ReturnInfo(), 'db_size': 0}),
    # один элемент с метаданными
    ([[FULL_INSTANCE1]], {'exception': False, 'db_size': 1}),
    # один элемент без метаданных
    ([[INSTANCE_WO_METADATA]], {'exception': False, 'db_size': 1}),
    # один элемент без идентификатора
    ([[INSTANCE_WO_ID]], {'exception': True, 'db_size': 0}),
    # один элемент без ебмеддинга
    ([[INSTANCE_WO_EMBEDDING]], {'exception': True, 'db_size': 0}),
    # несколько элементов
    ([[FULL_INSTANCE1,FULL_INSTANCE2]], {'exception': False, 'db_size': 2}),
    # дубликаты в списке
    ([[FULL_INSTANCE1,FULL_INSTANCE1]], {'exception': True, 'db_size': 0}),
    # элемент существует в бд (по id)
    ([[FULL_INSTANCE1],[FULL_INSTANCE1]], {'exception': False, 'db_size': 1}),
    # неверный формат идентикатора 1
    ([[INSTANCE_WITH_BAD_ID1]],{'exception': True, 'db_size': 0}),
    # неверный формат идентификатора 2
    ([[INSTANCE_WITH_BAD_ID2]],{'exception': True, 'db_size': 0}),
    # неверный формат идентификатора 3
    ([[INSTANCE_WITH_BAD_ID3]],{'exception': True, 'db_size': 0})
    ]

VECTORDB_DELETE_TEST_CASES = [
    # пустой список
    ([FULL_INSTANCE1,FULL_INSTANCE2], [], {'exception': False, 'db_size': 2})
    # удаление одного существующего элемента
    ([FULL_INSTANCE1,FULL_INSTANCE2], ['456'], {'exception': False, 'db_size': 1}),
    # удаление одного несуществующего элемента
    ([FULL_INSTANCE1,FULL_INSTANCE2], ['789'], {'exception': False, 'db_size': 2}),
    # в списке элементов на удаление есть несуществующие
    ([FULL_INSTANCE1,FULL_INSTANCE2], ['456','789'], {'exception': False, 'db_size': 1}),
    # в списке элементов на удаление все существуют
    ([FULL_INSTANCE1,FULL_INSTANCE2], ['123','456'], {'exception': False, 'db_size': 0}),
    #неверный формат идентификаторов 1
    ([FULL_INSTANCE1,FULL_INSTANCE2], [123], {'exception': True, 'db_size': 2}),
    # неверный формат идентификатора 2
    ([FULL_INSTANCE1,FULL_INSTANCE2], [True], {'exception': True, 'db_size': 2}),
    # неверный формат идентификатора 3
    ([FULL_INSTANCE1,FULL_INSTANCE2], [None], {'exception': True, 'db_size': 2}),
]

VECTORDB_READ_TEST_CASES = [
    # пустой список
    ([[FULL_INSTANCE1,FULL_INSTANCE2]], [], {'exception': False, 'output_ids': []}),
    # один существующий элемент
    ([[FULL_INSTANCE1,FULL_INSTANCE2]], ['123'], {'exception': False, 'output_ids': ['123']}),
    # один несуществующий элемент
    ([[FULL_INSTANCE1,FULL_INSTANCE2]], ['789'], {'exception': False, 'output_ids': [None]}),
    # несколько существующих элементов
    ([[FULL_INSTANCE1,FULL_INSTANCE2]], ['123', '456'], {'exception': False, 'output_ids': ['123','456']}),
    # в списке есть несуществующий элемент
    ([[FULL_INSTANCE1,FULL_INSTANCE2]], ['123', '789'], {'exception': False, 'output_ids': ['123',None]})
    #неверный формат идентификаторов 1
    ([[FULL_INSTANCE1,FULL_INSTANCE2]], [123], {'exception': True, 'output_ids': []}),
    # неверный формат идентификатора 2
    ([[FULL_INSTANCE1,FULL_INSTANCE2]], [True], {'exception': True, 'output_ids': []}),
    # неверный формат идентификатора 3
    ([[FULL_INSTANCE1,FULL_INSTANCE2]], [None], {'exception': True, 'output_ids': []}),
]

VECTORDB_RETRIEVE_TEST_CASES = [
    # ретрив по одному квери
    ([FULL_INSTANCE1,FULL_INSTANCE2], [FULL_INSTANCE1], 1, {'exception': False, 'output_size': [1]}),
    # ретрив по нескольким квери
    ([FULL_INSTANCE1,FULL_INSTANCE2], [FULL_INSTANCE1, FULL_INSTANCE1], 1, {'exception': False, 'output_size': [1, 1]}),
    # в бд меньше элементов, чем заданное количество
    ([FULL_INSTANCE1], [FULL_INSTANCE1], 2, {'exception': False, 'output_size': [1]}),
    # torch-тип данных эмбеддинга
    ([FULL_INSTANCE1,FULL_INSTANCE2], [INSTANCE_WITH_TORCH_EMB], 2, {'exception': False, 'output_size': [1]}),
    # numpy-тип данных эмбеддинга
    ([FULL_INSTANCE1,FULL_INSTANCE2], [INSTANCE_WITH_NUMPY_EMB], 2, {'exception': False, 'output_size': [1]}),
    # неверный формат ембеддинга квери # 1
    ([FULL_INSTANCE1,FULL_INSTANCE2], [INSTANCE_WITH_BAD_EMB1], 2, {'exception': True, 'output_size': [-1]}),
    # неверный формат ембеддинга квери # 2
    ([FULL_INSTANCE1,FULL_INSTANCE2], [INSTANCE_WITH_BAD_EMB2], 2, {'exception': True, 'output_size': [-1]}),
    # неверный формат ебмеддинга квери # 3
    ([FULL_INSTANCE1,FULL_INSTANCE2], [INSTANCE_WITH_BAD_EMB2], 2, {'exception': True, 'output_size': [-1]}),
]

VECTORDV_COUNT_TEST_CASES = [
    # нуль элементов
    ([], 0),
    # один Элемент
    ([FULL_INSTANCE1], 1),
    # несколько элементов
    ([FULL_INSTANCE1,FULL_INSTANCE2], 2),
]

VECTORDB_EXIST_TEST_CASES = [
    # элемент существует
    ([FULL_INSTANCE1,FULL_INSTANCE2], '123', {'exception': False, 'exist': True})
    # элемента не существует
    ([FULL_INSTANCE1,FULL_INSTANCE2], '789', {'exception': False, 'exist': False})
    # неверный формат идентификатора # 1
    ([FULL_INSTANCE1,FULL_INSTANCE2], 789, {'exception': True, 'exist': False})
    # неверный формат идентификатора # 2
    ([FULL_INSTANCE1,FULL_INSTANCE2], False, {'exception': True, 'exist': False})
    # неверный формат идентификатора # 3
    ([FULL_INSTANCE1,FULL_INSTANCE2], None, {'exception': True, 'exist': False})
]

VECTORDB_CLEAR_TEST_CASES = [
    # чистка пустой бд
    [],
    # чиста бд с одним элементов
    [FULL_INSTANCE1],
    # чиста бд с несколькими элементами
    [FULL_INSTANCE1,FULL_INSTANCE2]
]
