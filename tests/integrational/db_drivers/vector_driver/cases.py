from chromadb.errors import ChromaError

import sys
sys.path.insert(0, "../../../")
from src.db_drivers.vector_driver import VectorDBInstance
from src.utils.errors import ReturnInfo

FULL_INSTANCE1 = VectorDBInstance(id='123', document='qwerty', embedding=[0.1,0.2,0.3], metadata={'k1': 'v1'})
FULL_INSTANCE2 = VectorDBInstance(id='456', document='ytrewq', embedding=[0.4,0.5,0.6], metadata={'k2': 'v2'})
INSTANCE_WO_METADATA = VectorDBInstance(id='456', document='ytrewq', embedding=[0.4,0.5,0.6])
INSTANCE_WO_ID = VectorDBInstance(document='ytrewq', embedding=[0.4,0.5,0.6])
INSTANCE_WO_EMBEDDING = VectorDBInstance(id='456', document='ytrewq')

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
    () # TODO
    # неверный формат идентификатора 2
    () # TODO
    ]

VECTORDB_DELETE_TEST_CASES = [
    # пустой список
    ()
    # удаление одного существующего элемента
    (),
    # удаление одного несуществующего элемента
    # в списке элементов на удаление есть несуществующие
    # в списке элементов на удаление все существуют
    #неверный формат идентификаторов 1
    # неверный формат идентификатора 2
]

VECTORDB_READ_TEST_CASES = [
    # пустой список
    # один существующий элемент
    # один несуществующий элемент
    # несколько существующих элементов
    # в списке есть несуществующий элемент
    # неверный формат идентификатора 1
    # неверный формат идентификатора 2
]

VECTORDB_RETRIEVE_TEST_CASES = [
    # ретрив по одному квери
    # ретрив по нескольким квери
    # в бд меньше элементов, чем заданное количество
    # в бд больше элементов, чем заданное количество
]

VECTORDV_COUNT_TEST_CASES = [
    # нуль элементов
    # один Элемент
    # несколько элементов
]

VECTORDB_EXIST_TEST_CASES = [
    # элемент существует
    # элемента не существует
]

VECTORDB_CLEAR_TEST_CASES = [
    # чистка пустой бд
    # чиста бд с одним элементов
    # чиста бд с несколькими элементами
]
